import json
import random
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

# Initialize the Inky Impression 7-Color display
inky_display = auto()
inky_display.set_border(inky_display.WHITE)

# Path to the Bible verses JSON file (list of strings in "Book Chapter:Verse - text" format)
BIBLE_VERSES_FILE = "bible_verses.json"

def load_verses():
    """Load Bible verses from a JSON file."""
    try:
        with open(BIBLE_VERSES_FILE, "r", encoding="utf-8") as file:
            verses = json.load(file)
        return verses
    except Exception as e:
        print("Error loading Bible verses:", e)
        return []

def get_random_verse(verses):
    """Select and split a random Bible verse from the loaded data."""
    if not verses:
        return "No verses found.", "Please check the JSON file."
    verse_line = random.choice(verses)
    try:
        reference, verse_text = verse_line.split(" - ", 1)
    except ValueError:
        reference = ""
        verse_text = verse_line
    return reference, verse_text

def process_image(image_path, size=(50, 50)):
    """
    Load an image, convert it to RGBA (to support transparency), and resize it.
    No color conversion is applied.
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        img.thumbnail(size, Image.ANTIALIAS)
        return img
    except Exception as e:
        print(f"Error loading image {image_path}:", e)
        return None

def display_verse():
    """Render the Bible verse and additional graphics onto the Inky display."""
    # Load a random Bible verse
    verses = load_verses()
    reference, verse_text = get_random_verse(verses)
    
    # Create a blank canvas with the display's dimensions (in palette mode "P")
    img = Image.new("P", (inky_display.width, inky_display.height), color=inky_display.WHITE)
    draw = ImageDraw.Draw(img)
    
    # Load fonts (using system DejaVu fonts; adjust paths if necessary)
    font_title   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    font_body    = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    font_blessed = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    font_symbols = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    
    # ---------------------------
    # Top Left: Display the Canadian Flag
    # ---------------------------
    flag = process_image("canada_flag.png", size=(60, 40))
    if flag:
        # Paste the flag using its alpha channel as mask
        img.paste(flag, (10, 10), flag)
    
    # ---------------------------
    # Top Middle: Display the Dove Image
    # ---------------------------
    dove = process_image("dove.png", size=(50, 50))
    if dove:
        dove_x = (inky_display.width - dove.width) // 2  # Center horizontally
        dove_y = 10  # 10 pixels from the top
        # Paste the dove WITHOUT the mask parameter so it displays as-is.
        img.paste(dove, (dove_x, dove_y))
    
    # ---------------------------
    # Top Right: Draw Three Cross Symbols (Black)
    # ---------------------------
    cross_text = "✝  ✝  ✝"
    cross_width, _ = draw.textsize(cross_text, font=font_symbols)
    cross_x = inky_display.width - cross_width - 10  # 10 pixels from right edge
    cross_y = 10  # 10 pixels from top
    draw.text((cross_x, cross_y), cross_text, inky_display.BLACK, font=font_symbols)
    
    # ---------------------------
    # Center: Bible Verse Text (Reference and Verse)
    # ---------------------------
    full_text = f"{reference}\n\n{verse_text}"
    max_text_width = inky_display.width - 40  # 20 pixels padding on each side
    lines = []
    for paragraph in full_text.split("\n"):
        words = paragraph.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_width, _ = draw.textsize(test_line, font=font_body)
            if test_width <= max_text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        lines.append("")  # Add an empty line between paragraphs
    if lines and lines[-1] == "":
        lines.pop()  # Remove the last empty line
    
    line_height = font_body.getsize("Ay")[1] + 5
    text_block_height = len(lines) * line_height
    start_y = (inky_display.height - text_block_height) // 2
    for i, line in enumerate(lines):
        line_width, _ = draw.textsize(line, font=font_body)
        x = (inky_display.width - line_width) // 2  # Center the line horizontally
        y = start_y + i * line_height
        draw.text((x, y), line, inky_display.BLACK, font=font_body)
    
    # ---------------------------
    # Bottom: "Blessed Day" Message in Blue (using Inky's built-in BLUE)
    # ---------------------------
    blessed_message = "Have A Blessed Day!!!"
    blessed_width, blessed_height = draw.textsize(blessed_message, font=font_blessed)
    blessed_x = (inky_display.width - blessed_width) // 2
    blessed_y = inky_display.height - blessed_height - 10  # 10 pixels from the bottom
    draw.text((blessed_x, blessed_y), blessed_message, inky_display.GREEN, font=font_blessed)
    
    # ---------------------------
    # Update the Display
    # ---------------------------
    inky_display.set_image(img)
    inky_display.show()

if __name__ == "__main__":
    display_verse()
