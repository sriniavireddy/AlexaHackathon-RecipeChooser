import json
import requests

#API_BASE="http://bartjsonapi.elasticbeanstalk.com/api"
def recipe_choose_handler(event, context):
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
	intent = intent_request["intent"]
	intent_name = intent_request["intent"]["name"]
	if intent_name == "GetRecipeNameIntent":
		return get_recipe_name(intent_request['intent'])
	elif intent_name == "TellMeMoreIntent":
		return get_description(intent_request['intent'],session)
	elif intent_name == "TellMeIngredientsIntent":
		return get_ingredients(intent_request['intent'])
	elif intent_name == "TellMeStepsIntent":
		return tell_steps(intent_request['intent'],session)
	elif intent_name == "RepeatIntent":
		return repeat_step(intent_request['intent'],session)
	elif intent_name == "AMAZON.HelpIntent":
		return get_welcome_response()
	elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
		return handle_session_end_request()
	else:
		raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Recipe chooser - Thanks"
    speech_output = "Thank you for using the Recipe Chooser skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "RecipeChooser"
    speech_output = "Welcome to the Alexa Recipe chooser skill. " \
                    "You can ask me for recipe names "
    reprompt_text = "Please ask me for recipe names, " \
                    "for example egg fry."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_description(intent,session):
	session_attributes = {}
	card_title = "Recipe description"
	reprompt_text = ""
	should_end_session = False
	speech_output = ""

	desc_file = open("description.txt", "r")
	description_dict = dict()
	for desc in desc_file.readlines():
		desc_parts = desc.strip().split(",")
		recipe = {}
		recipe['name'] = desc_parts[0]
		recipe['calories'] = desc_parts[1]
		recipe['time'] = desc_parts[2]
		description_dict[desc_parts[0].lower()] = recipe

	input_recipe = intent['slots']['Recipe']['value'].lower()
	if  input_recipe in description_dict:
		speech_output =  description_dict[input_recipe]['name'] + " has " + description_dict[input_recipe]['calories'] +  " calories." + "It will take " + description_dict[input_recipe]['time'] + " to complete this recipe."
	else:
		speech_output = "sorry, I did not find information about the recipe you asked for"
		reprompt_text = "Can you please try again ?"


	return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_recipe_name(intent):
    session_attributes = {}
    card_title = "Recipe name"
    reprompt_text = ""
    should_end_session = False
    ingredient = intent['slots']['Ingredient']['value']
    speech_output = "These are some recipes you can cook with " + ingredient + "."
    recipes, session_attributes = get_recipe_names(ingredient, session_attributes)
    speech_output +=  "They are  "+ ",".join(recipes)
    print "session attributes", session_attributes.keys()
    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_recipe_names(ingredient,session_attributes):
	API_KEY = "392b0844b799b512a189576d9fef8b04"
	APP_ID = "c9edeeaf"
	API_URL = "https://api.edamam.com/search?q={0}&app_id={1}&app_key={2}"

	result = requests.get(API_URL.format(ingredient, APP_ID, API_KEY))
	recipes = []
	if result is not None:
		result_json = result.json()
		hits = result_json['hits']
		session_attributes = hits
		for hit in hits:
			recipe = hit['recipe']
			print recipe['label']
			recipes.append(recipe['label'])
	for r in recipes:
		print r

	return recipes, {"hits": session_attributes}


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

def get_ingredients(intent):
	session_attributes = {}
	card_title = "Recipe Ingredients"
	reprompt_text = "Say tell me the steps for the recipe and I will tell you the steps."
	should_end_session = False
	speech_output = ""

	ingredient_file = open("ingredients.txt", "r")
	ingredients_dict = dict()
	for ing in ingredient_file.readlines():
		ing_parts = ing.strip().split(",")
		recipe = {}
		recipe['name'] = ing_parts[0]
		recipe['ingredients']= []
		recipe['ingredients'].append(ing_parts[1])
		recipe['ingredients'].append(ing_parts[2])
		ingredients_dict[ing_parts[0].lower()] = recipe

	input_recipe = intent['slots']['Recipe']['value'].lower()
	if  input_recipe in ingredients_dict:
		speech_output =  "ingredients are " + ",".join(ingredients_dict[input_recipe]['ingredients']) + "."
	else:
		speech_output = "sorry, I did not find information about the recipe you asked for"
		reprompt_text = "Can you please try again ?"


	return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def tell_steps(intent, session):
	print session
	session_attributes = {}
	card_title = "Recipe Steps"
	input_recipe = ""
	if "recipe_name" not in session['attributes']:
		input_recipe = intent['slots']['Recipe']['value'].lower()
	else:
		input_recipe = session['attributes']['recipe_name']

	steps = []
	for step in open(input_recipe+".txt","r").readlines():
		steps.append(step)
	reprompt_text = "Say next for next step"

	if "step_number" not in session['attributes']:
		step_number = 0
	else:
		step_number = session['attributes']['step_number']
	speech_output = steps[step_number] + "."
	attr = {"step_number" : step_number + 1, "recipe_name" : input_recipe, "step_text": speech_output}
	session_attributes = attr

	reprompt_text = "Say next step, to read the next step or you can say repeat to repeat the step again"

	should_end_session = False
	if step_number == len(steps):
		should_end_session = True

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def repeat_step(intent, session):

	card_title = "Recipe repeat Step"
	speech_output = session['attributes']['step_text']
	attr = {"step_number" : session['attributes']['step_number'], "recipe_name" : session['attributes']['recipe_name'], "step_text": speech_output}
	session_attributes = attr

	reprompt_text = "Say next step, to read the next step or you can say repeat to repeat the step again"
	should_end_session = False

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))
