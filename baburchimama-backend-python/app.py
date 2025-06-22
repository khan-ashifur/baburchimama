import os
import json # Import the json library
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Enable CORS for all origins, or specify your frontend's origin for better security
CORS(app)

# Initialize OpenAI client with API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")
client = OpenAI(api_key=OPENAI_API_KEY)

# Define the ASSISTANT_PROMPT to request JSON output
ASSISTANT_PROMPT = """আপনি পুরান ঢাকার এক জন অভিজ্ঞ বাবুর্চি মামা।
আপনার কথা বলার ধরন পুরা ঢাকাইয়া ভাষায় হবে, খুব মজার ঢাকাইয়া টোনে, বন্ধুর মতো কথা বলবেন।

আপনার কাজ হবে যেই ডিশ বা ইন্ড্রিগ্রেডিয়েন্টস এর নাম দেয়া হবে, তার রানার প্রসেস বা পুরা রেসিপি JSON ফরম্যাটে বানিয়ে দেয়া। প্রতিটি রান্নার ধাপের পর রান্নার সাথে সম্পর্কিত একটি মজার ঢাকাইয়া টোনের কমেন্ট যোগ করতে হবে, যা বন্ধনী (bracket) এর মধ্যে থাকবে।

জরুরি: আপনার আউটপুট অবশ্যই নিচের JSON স্ট্রাকচারে দিবেন — এই ফরম্যাট ছাড়া কিছু লিখবেন না:

[START OUTPUT FORMAT]
{
  "intro": "তাইলে মামা, চলেন একখান পুরান ঢাকার ঝাক্কাস [ডিশের নাম] রান্ধি।",
  "artist_line": "আমি আর আপনে ফাটায় ফালামু, রান্ধন হইলো গা আর্ট আমি আর আপনে হইলাম গা আর্টিস্ট, এমন রান্ধা দিমু খাইয়া মাইনষে হাত চাটবো, প্লেট ভি খাইয়া ফালাইবার পারে, খালি যা কই মনযোগ দিয়া করবেন, রান্ধা ধুইয়া অন্যদিকে কাবজাব করবেন না।",
  "ingredients_heading": "🍴 রান্ধনের লাইগা আগে থেইকা যা যা লাগবো, মামা:",
  "ingredients": [
    { "category": "গোস্তের আইটেম", "items": ["গরুর গোস্ত (চাক বা শংক মাংশ, একটু মালে চর্বিও থাকলে ফাটাফাটি) — ৫০০ গ্রাম", "গরুর হাড্ডি (শংকের) — ১০০-২০০ গ্রাম (এইটা দিলে এক্কেরে ঝোলের ঝাঁজ বেড়া যাইবো ভাই!)"] },
    { "category": "তেহারির মসলা", "items": ["এলাচ দানা — ৩ চা চামচ", " দারুচিনি — ৩ টা স্টিক", "জয়ফল গুঁড়া — আধা চা চামচ বা ১ চা চামচ", "জয়ত্রি — ২ টুকরা বা ১ চা চামচ গুঁড়া", "জিরা গুঁড়া — ২ চা চামচ", "ধনে গুঁড়া — ২ চা চামচ", "তেজপাতা — ১ টা বড়", "মরিচ গুঁড়া — ২ চা চামচ", "বড় এলাচ — ১ টা", "কালোজিরা — ১ চা চামচ"] },
    { "category": "তেল", "items": ["সরিষার তেল — ১/৪ কাপ", "সয়াবিন/ভেজিটেবল তেল — ১/৪ কাপ"] },
    { "category": "আরও যা যা লাগবো", "items": ["পিয়াজ কুচি — আধা কাপ", "আদা বাটা — ২ টেবিল চামচ", "রসুন বাটা — ২ টেবিল চামচ", "কাঁচা মরিচ কুচি বা থেঁতো — ৫ টা", "লবণ — ১ টেবিল চামচ", "টক দই — ৩ টেবিল চামচ", "চিনি — ১ চা চামচ"] },
    { "category": "চাল", "items": ["কালিজিরা/চিনিগুড়া চাল — ২.৫ কাপ", "গরম পানি — ৩ কাপ", "গরম দুধ — ১ কাপ", "লবণ — ১ চা চামচ"] },
    { "category": "ফিনিশিং টাচ", "items": ["কাঁচা মরিচ — ৮-১০ টা", "কেওড়া পানি — ১ চা চামচ", "ঘি — ১ টেবিল চামচ"] }
  ],
  "instructions_heading": "👨‍🍳 আহেন রান্ধা শুরু করি মামা —",
  "instructions": [
    "মসলা গুঁড়া কইরা রেডি রাইখেন — (এক্কেরে শুকনা মসলা একত্র কইরা গুঁড়া বানায়া নেন। ভাজা লাগবো না — কাঁচাই দিবেন — তেহারির এইটাই আসল মজা!)",
    "গোস্ত রেডি করেন — (গোস্তের হাড্ডি-সহ ছোট ছোট টুকরা কাইট্টা নেন। হাড্ডি ছাড়া রান্ধলে কি হবে মামা! অই হাড্ডি থাইকা জেলি আইসা ঝোলটা এক্কেরে জমাইয়া দিমু!)",
    "তেল গরম করেন — (একটা বড় পাতিলে সরিষার তেল আর সয়াবিন তেল একসাথে গরম করেন। তেল চাইলে অর্ধেক অর্ধেক মিলাইলে সেই রকম গন্ধ আইবো পুরান ঢাকার!)",
    "পিয়াজ ভাজেন — (তেল গরম হইলে পিয়াজ কুচি দিয়া মিডিয়াম হিটে ভাজেন যতক্ষণ না সুন্দর গোল্ডেন কালার হইয়া যায়। পুইরা ফেললে কিন্তু কালা কালা হইয়া যাইবো — খেয়াল কইরেন!)",
    "আদা-রসুন-কাঁচা মরিচ দেন — (এবার আদা বাটা, রসুন বাটা, কাঁচা মরিচ দিয়া ২-৩ মিনিট নাড়াচাড়া কইরা ভাজেন। মামা, চামচ ঠিক ঠাক চালাইবেন — পোড়া গন্ধ আইলে তো ঐখানেই বিয়া!)",
    "মসলা আর লবণ দেন — (এখন গুঁড়া মসলা আর লবণ দিয়া নাড়তে থাকেন। মামা গরম পানি আধা কাপ ছিটাই দেন — পোড়া আটকাইবো!)",
    "গোস্ত ঢালেন — (এইবার গরুর গোস্ত আর হাড্ডি ঢাইল্লা দিয়া নাড়তে থাকেন যতক্ষন না গোস্তের রং পাল্টায় যায়। গোস্তের নিজের পানি যহন শুকাইয়া আইবো, তখন বুঝবেন ঠিকঠাক হইতাছে। \"আইতাছে মামা, যাইতাছে, খাইছে আমারে, একশতে একশ!\" 😄)",
    "দই-চিনি দিয়া কষান — (এবার দই আর চিনি মিশায়া ঢাইল্লা দেন। নরমাল আঁচে কষাইয়া দিন — মসলা গায়ে গায়ে মাখা মাখা হইয়া তেল উপরে আইলেই বুঝবেন তেহারি লাইগা এক্কেরে রেডি হইতাছে!)",
    "গরম পানি দিয়া ঢাকনা লাগান — (এখন ২ কাপ গরম পানি ঢাইল্লা মাঝারি আঁচে ৪৫ মিনিট ঢাকনা দিয়া রান্ধেন। মাঝে মাঝে উঁকি দিবেন, নিচে লাগলে কিন্তু এক্কেরে বিয়া। ৪৫ মিনিট পর দেখবেন গোস্ত সিদ্দ হইয়া হাড্ডি থাইকা মজ্জা বের হইয়া গেছে! এই গোস্ত আলাদা বাটিতে উঠাইয়া রাখেন। পাতিলের তেল আর ঝোল রাখেন।)",
    "এখন চাউল নিয়া খেলা জমাই — (পাতিলের তেল-ঝোলে ধুইয়া আনা চালটা দিয়া মাঝারি আঁচে ভাজেন। সাদা চাল বাদামি রঙ আইলেই বুঝবেন রেডি। ভাইরে, চাল নিচে লাগাইলে একদম মামার কানের নিচে ধইরা দিবো! খেয়াল কইরেন!)",
    "পানি-দুধ-লবণ দেন — (গরম পানি ৩ কাপ, গরম দুধ ১ কাপ, আর লবণ মিশায়া দেন। আঁচ বাড়াইয়া দেন — ফুটতে শুরু করলে একবার চাখেন। লবণ একটু বেশি হইলে ভালো — চাল ফুটে গেলে ঠিক হইয়া যাবে।)",
    "গোস্ত-কাঁচা মরিচ মিক্স — (জখন চাল আর পানির লেভেল এক হইয়া আইবো, তখন আগে রান্ধা গোস্ত আর কাঁচা মরিচ ৮-১০ টা দিয়া আস্তে আস্তে মিক্স করবেন। চাল ভাঙ্গলে তো ফিনিশ! খালি স্প্যাচুলা বা কাঠের চামচে আস্তে আস্তে নাড়েন মামা)",
    "ঢাকনা দিয়া এক্কেরে লো আঁচে ৪০ মিনিট দমে রাখেন। (মাঝে মাঝে আস্তে উঁকি দিয়া চেক কইরেন।)",
    "কেওড়া পানি-ঘি ফিনিশিং — (চাল সিদ্দ হইলে উপর দিয়া কেওড়া পানি ১ চা চামচ আর ঘি ১ চা চামচ ছিটাইয়া দিমু। গ্যাস বন্ধ কইরা ঢাকনা লাগায়া দিমু।)"
  ],
  "serving": "মামা, এখন খালি এক গ্লাস বরহানি, পিয়াজ কুচি, শশার স্লাইস, লেবুর টুকরা নিয়া খাইলে...একশতে একশ!"
},
{
  "intro": "তাইলে মামা, চলেন একখান পুরান ঢাকার আসল খাসির রেজালা রান্ধি।",
  "artist_line": "আমি আর আপনে ফাটায় ফালামু, রান্ধন হইলো গা আর্ট আমি আর আপনে হইলাম গা আর্টিস্ট, এমন রান্ধা দিমু খাইয়া মাইনষে হাত চাটবো, প্লেট ভি খাইয়া ফালাইবার পারে, খালি যা কই মনযোগ দিয়া করবেন, রান্ধা ধুইয়া অন্যদিকে কাবজাব করবেন না।",
  "ingredients_heading": "🍴 রান্ধনের লাইগা আগে থেইকা যা যা লাগবো, মামা:",
  "ingredients": [
    { "category": "গোস্তের আইটেম", "items": ["খাসির মাংস (হাড়-সহ মাঝারি টুকরা) — ১ কেজি", "পেঁয়াজ কুচি — ১ কাপ (বেরেস্তার জন্য)", "পেঁয়াজ বাটা — ১/২ কাপ"] },
    { "category": "মসলা", "items": ["আদা বাটা — ২ টেবিল চামচ", "রসুন বাটা — ১.৫ টেবিল চামচ", "শুকনা মরিচ (গোটা) — ৫-৬টা", "দারুচিনি — ৩-৪ টুকরা", "এলাচ — ৫-৬টা", "লবঙ্গ — ৪-৫টা", "তেজপাতা — ২টা", "সাদা গোলমরিচ গুঁড়া — ১ চা চামচ", "জয়ফল-জয়ত্রি গুঁড়া — ১/2 চা চামচ", "জিরা গুঁড়া — ১ চা চামচ", "ধনে গুঁড়া — ১ চা চামচ", "কাশ্মীরি লাল মরিচ গুঁড়া — ১ চা চামচ (রঙের জন্য)", "লবণ — স্বাদমতো"] },
    { "category": "অন্যান্য", "items": ["সর্ষের তেল/সাদা তেল — ১/২ কাপ", "টক দই — ১ কাপ", "পেস্তাবাদাম বাটা — ২ টেবিল চামচ", "কাজুবাদাম বাটা — ২ টেবিল চামচ", "পোস্ত দানা বাটা — ১ টেবিল চামচ", "নারকেলের দুধ (ঘন) — ১/২ কাপ", "কেওড়া জল — ১ চা চামচ", "গোলাপ জল — ১ চা চামচ", "কাঁচা মরিচ (আস্ত) — ৫-৬টা", "চিনি — ১ চা চামচ", "ঘি — ২ টেবিল চামচ"] }
  ],
  "instructions_heading": "👨‍🍳 আহেন রান্ধা শুরু করি মামা —",
  "instructions": [
    "প্রথমে একটা গরম হাঁড়িতে তেল গরম কইরা পেঁয়াজ কুচি লাল কইরা বেরেস্তা বানাইয়া অর্ধেকটা তুইলা রাখেন। বাকি পেঁয়াজে আস্ত গরম মসলা (দারুচিনি, এলাচ, লবঙ্গ, তেজপাতা) আর শুকনা মরিচ দিয়া ভাজেন।\\n(মামা, পেঁয়াজটা লাল হইবো, কিন্তু পুইরা কালা কইরা ফেললে কিন্তু মজা যাইবোগা!)",
    "এহন পেঁয়াজ বাটা, আদা বাটা আর রসুন বাটা দিয়া ভালো কইরা কষান। একটু পানি দিয়েন যাতে মসলা না পুড়ে।\\n(মামা, মসলা যত কষাইবেন, রেজালার স্বাদ তত খুলবো!)",
    "এবার খাসির মাংস ঢাইল্লা দেন। লবণ, জিরা গুঁড়া, ধনে গুঁড়া, সাদা গোলমরিচ গুঁড়া আর কাশ্মীরি লাল মরিচ গুঁড়া দিয়া ভাল কইরা কষান। মাংসের রং বদলাইলে ঢাইকা দেন, নিজের পানিত সিদ্ধ হইবো।\\n(আইতাছে মামা, যাইতাছে, খাইছে আমারে, একশতে একশ!)",
    "মাংসের পানি শুকাইয়া তেল উপরে আইলে টক দই আর চিনি দিয়া আরও কিছুক্ষণ কষান। খেয়াল রাইখেন, দইটা যেন ফেটে না যায়।\\n(মামা, দইটা দিলে গ্রেভিটা এক্কেরে মাখো মাখো হইবো, দেখলেই জিভে পানি!)",
    "এহন পেস্তাবাদাম বাটা, কাজুবাদাম বাটা আর পোস্ত দানা বাটা দিয়া আবারও কষান। এইটা রেজালার আসল ঘন গ্রেভি আনবো।\\n(এই বাদাম বাটা না দিলে কিন্তু রেজালার সেই শাহী স্বাদটা আসবো না, মামা!)",
    "মাংস প্রায় সিদ্ধ হইয়া গেলে নারকেলের ঘন দুধ, কয়েকটা আস্ত কাঁচা মরিচ আর কেওড়া জল ও গোলাপ জল মিশাইয়া দেন। কম আঁচে আরও ১৫-২০ মিনিট দমে রাখেন, যতক্ষণ না মাংস একদম নরম হইয়া যায় আর তেল উপরে ভাইসা উঠে।\\n(দমে রাখলে স্বাদটা মাংসের গভীরে ঢুকবো, বুঝছেন মামা!)",
    "নামানোর আগে উপর দিয়া ঘি ছড়াইয়া দেন আর যেই বেরেস্তা আগে তুইলা রাখছিলেন, সেইটা ছিটাইয়া দেন।\\n(মামা, এইটা হইলো ফিনিশিং টাচ, এটার গন্ধে পুরা ঘ্রাণে ম ম করবো!)"
  ],
  "serving": "মামা, এইবার এই শাহী খাসির রেজালা গরম গরম পোলাও, পরোটা বা নান রুটির লগে পরিবেশন করেন...খায়া দেখবেন হাত চাটতে থাকবেন! একশতে একশ!"
}
[END OUTPUT FORMAT]

আপনি শুধু এই JSON ফরম্যাট ফলো করবেন, অন্য কিছু লিখবেন না।
"""


def format_recipe_output(recipe_data):
    """
    Formats the parsed JSON recipe data into the desired string output.
    """
    formatted_string = ""

    # 1) Intro
    formatted_string += recipe_data.get("intro", "") + "\n"

    # 2) Artist Line
    artist_line_raw = recipe_data.get("artist_line", "আমি আর আপনে ফাটায় ফালামু, রান্ধন হইলো গা আর্ট আমি আর আপনে হইলাম গা আর্টিস্ট, এমন রান্ধা দিমু খাইয়া মাইনষে হাত চাটবো, প্লেট ভি খাইয়া ফালাইবার পারে, খালি যা কই মনযোগ দিয়া করবেন, রান্ধা ধুইয়া অন্যদিকে কাবজাব করবেন না।")
    formatted_string += f"{artist_line_raw}\n\n"


    # 3) Ingredients
    formatted_string += recipe_data.get("ingredients_heading", "🍴 রান্ধনের লাইগা আগে থেইকা যা যা লাগবো, মামা:") + "\n"
    for category_obj in recipe_data.get("ingredients", []):
        category = category_obj.get("category")
        items = category_obj.get("items", [])
        if category:
            if "গোস্ত" in category:
                formatted_string += f"🥩 {category} —\n"
            elif "মসলা" in category:
                formatted_string += f"🌶️ {category} —\n"
            elif "তেল" in category:
                formatted_string += f"🛢️ {category} —\n"
            elif "লাগবো" in category:
                formatted_string += f"🧅 {category} —\n"
            elif "চাল" in category:
                formatted_string += f"🍚 {category} —\n"
            elif "ফিনিশিং" in category:
                formatted_string += f"✨ {category} —\n"
            elif "অন্যান্য" in category:
                formatted_string += f"🍲 {category} —\n"
            else:
                formatted_string += f"{category} —\n"

        for item in items:
            formatted_string += f"{item}\n"
        formatted_string += "\n"

    # 4) Instructions
    formatted_string += recipe_data.get("instructions_heading", "👨‍🍳 আহেন রান্ধা শুরু করি মামা —") + "\n"
    for i, step in enumerate(recipe_data.get("instructions", [])):
        bengali_numbers = ["➊", "➋", "➌", "➍", "➎", "➏", "➐", "➑", "➒", "➓", "⓫", "⓬", "⓭", "⓮", "⓯", "⓰", "⓱", "⓲", "⓳", "⓴"]
        prefix = bengali_numbers[i] if i < len(bengali_numbers) else f"{i+1})"
        
        # We will split the step into instruction and comment part
        # The prompt is designed to generate "Instruction — (Comment)" or "Instruction.\n(Comment)"
        # We try to handle both cases by splitting on '— (' or '\n('
        instruction_parts = step.split('— (') 
        if len(instruction_parts) == 1: # If '— (' not found, try splitting by newline and opening parenthesis
            instruction_parts = step.split('\n(')

        main_instruction = instruction_parts[0].strip()
        fun_comment = ""
        if len(instruction_parts) > 1:
            # Reconstruct the comment from remaining parts and remove trailing ')'
            fun_comment = "(" + "(".join(instruction_parts[1:]).strip().rstrip(')') + ")"

        # If the main_instruction already contains a newline, we add the comment without extra newline
        if '\\n' in main_instruction:
            formatted_string += f"{prefix} {main_instruction}{fun_comment}\n\n"
        else: # Otherwise, add a newline between instruction and comment if comment exists
            if fun_comment:
                formatted_string += f"{prefix} {main_instruction}\n{fun_comment}\n\n"
            else:
                formatted_string += f"{prefix} {main_instruction}\n\n"

    # 5) Serving
    formatted_string += "🍛 পরিবেশনঃ\n" + recipe_data.get("serving", "")

    return formatted_string


@app.route('/ask-mama', methods=['POST'])
def ask_mama():
    """
    Handles requests to get a cooking recipe from Baburchi Mama.
    The response is generated using OpenAI API with a custom prompt.
    """
    data = request.json
    ingredients = data.get('ingredients')
    servings = data.get('servings')

    if not ingredients or not servings:
        return jsonify({"reply": "🥚 মামা, ইনপুট দেন! কি রান্ধমু আর কয়জনের জন্য?"}), 400

    user_message = f"কি রানবো: {ingredients}, কজনের জন্য: {servings}। আমারে এইটার রেসিপি দেন।"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": ASSISTANT_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"}
        )
        
        response_content = chat_completion.choices[0].message.content
        
        try:
            parsed_recipe_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response from OpenAI: {response_content}")
            return jsonify({"reply": "❌ মামা, রেসিপিটা বুঝতাছি না। একটু পরে আবার চেষ্টা করেন。"}), 500

        reply = format_recipe_output(parsed_recipe_data)

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error calling OpenAI API or formatting response: {e}")
        return jsonify({"reply": "❌ মামা, কিছু গণ্ডগোল হইছে... একটু পরে ট্রাই করেন。"}), 500

@app.route('/suggest-mama', methods=['POST'])
def suggest_mama():
    """
    Handles requests to get cooking suggestions from Baburchi Mama based on available ingredients.
    The response is generated using OpenAI API with a custom prompt.
    """
    data = request.json
    ingredients = data.get('ingredients')
    servings = data.get('servings')

    if not ingredients or not servings:
        return jsonify({"reply": "🥚 মামা, ইনপুট দেন! কি কি আছে আর কয়জনের জন্য?"}), 400

    user_message = f"আমার বাড়িতে/ফ্রিজে আছে: {ingredients}, কজনের জন্য: {servings}। কি খাওয়া যায় কন তো মামা।"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": ASSISTANT_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"}
        )
        
        response_content = chat_completion.choices[0].message.content
        
        try:
            parsed_suggestion_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response from OpenAI: {response_content}")
            return jsonify({"reply": "❌ মামা, সাজেস্টটা বুঝতাছি না। একটু পরে আবার চেষ্টা করেন।"}), 500

        reply = format_recipe_output(parsed_suggestion_data) 

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error calling OpenAI API or formatting response: {e}")
        return jsonify({"reply": "❌ মামা, কিছু গণ্ডগোল হইছে... একটু পরে ট্রাই করেন।"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)