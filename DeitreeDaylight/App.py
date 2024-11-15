import pygame
import cv2
import sys
import Script
from tkinter import filedialog
import threading
from os import path


if getattr(sys, 'frozen', False):
    # Use PyInstaller's _MEIPASS to find the asset directory
    base_path = sys._MEIPASS
else:
    # Use the normal directory structure during development
    base_path = path.abspath(".")

    
# Initialize Pygame
pygame.init()

TextBase = ["Placeholder: Deitree's Daylight.","Choose what You wish to purify,","and it shall be purified."]
# Screen dimensions
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
custom_font = pygame.font.Font(path.join(base_path, "data", "DQB2.ttf"), 26)
pygame.display.set_caption("Deitree's Daylight: Bring life back to Furrowfield")

# Load the icon image
icon_image = pygame.image.load(path.join(base_path, "data", "icon.png"))
# Set the window icon
pygame.display.set_icon(icon_image)

# Load video
video_path = path.join(base_path, "data","Deitree.mp4")
video = cv2.VideoCapture(video_path)

selected_button = pygame.image.load(path.join(base_path, "data","selected.png")).convert_alpha()
question_button = pygame.image.load(path.join(base_path, "data","question.png")).convert_alpha()
question2_button = pygame.image.load(path.join(base_path, "data","question2.png")).convert_alpha()

bg_image = pygame.image.load(path.join(base_path, "data","bg.png")).convert_alpha()
upText_image = pygame.image.load(path.join(base_path, "data","upText.png")).convert_alpha()
descText_image = pygame.image.load(path.join(base_path, "data","downText.png")).convert_alpha()

# Ensure the video opened successfully
if not video.isOpened():
    print("Error: Could not open video.")
    sys.exit()

# Button dimensions and properties
button_color = (0, 0, 0)
button_hover_color = (0, 0, 0)
button_width, button_height = 320, 45
loading_width, loading_height = 320, 30
button_font = pygame.font.Font(None, 36)

# Button positions
startP = 245

button1_rect = pygame.Rect((WIDTH-button_width)//8, startP, button_width, button_height)
button2_rect = pygame.Rect((WIDTH-button_width)//8, startP+50, button_width, button_height)
button3_rect = pygame.Rect((WIDTH-button_width)//8, startP+100, button_width, button_height)
button4_rect = pygame.Rect((WIDTH-button_width)//8, startP+150, button_width, button_height)

buttonConfirm_rect = pygame.Rect((WIDTH-button_width*2)//2, 500, button_width*2, button_height)

buttonFilePath_rect = pygame.Rect(((WIDTH-button_width*3)//2), 10, button_width*3, button_height*0.6)
buttonFilePathBeg_rect = pygame.Rect(((WIDTH-button_width*3)//2), 260, button_width*3, button_height*0.6)

button11_rect = pygame.Rect(((WIDTH-button_width)//8)+button_width+5, startP, button_height, button_height)
button22_rect = pygame.Rect(((WIDTH-button_width)//8)+button_width+5, startP+50, button_height, button_height)
button33_rect = pygame.Rect(((WIDTH-button_width)//8)+button_width+5, startP+100, button_height, button_height)
button44_rect = pygame.Rect(((WIDTH-button_width)//8)+button_width+5, startP+150, button_height, button_height)

button1q_rect = pygame.Rect(((WIDTH-button_width)//8)-button_height-5, startP, button_height, button_height)
button2q_rect = pygame.Rect(((WIDTH-button_width)//8)-button_height-5, startP+50, button_height, button_height)
button3q_rect = pygame.Rect(((WIDTH-button_width)//8)-button_height-5, startP+100, button_height, button_height)
button4q_rect = pygame.Rect(((WIDTH-button_width)//8)-button_height-5, startP+150, button_height, button_height)


buttonLoading1_rect = pygame.Rect(((WIDTH-loading_width)//2), 170, loading_width, loading_height)
buttonLoading2_rect = pygame.Rect(((WIDTH-loading_width)//2), 240, loading_width, loading_height)
buttonLoading3_rect = pygame.Rect(((WIDTH-loading_width)//2), 310, loading_width, loading_height)
buttonLoading4_rect = pygame.Rect(((WIDTH-loading_width)//2), 380, loading_width, loading_height)
buttonLoading5_rect = pygame.Rect(((WIDTH-loading_width)//2), 450, loading_width, loading_height)

fadeIn = True

surface_chunks = pygame.Surface((WIDTH, HEIGHT),pygame.SRCALPHA)
surface_chunks.set_alpha(80)
previous_number = 0

HEIGHT_CHUNK = HEIGHT//40

ButtonBooleans = [True,False,False,False]
selected_file_path = "Select file..."
# Set the video to loop by resetting its position
def reset_video(video):
    video.set(cv2.CAP_PROP_POS_FRAMES, 0)

def open_file_dialog(check):
    """Open a file dialog, filter by PNG, and ensure it starts with 'file'."""
    file_path = filedialog.askopenfilename(
        title="Select the furrowfield file",
        filetypes=[("Furrowfield .bin", "STGDAT02.bin")]  # Filter by .png extension
    )
    with open(file_path, 'rb') as f:
        binary_data = list(f.read())
    if list(binary_data[0:5]) == list([0x61, 0x65, 0x72, 0x43, 0xDD]):
        return file_path if file_path else "No file selected"
    if check:
        return "Select file..."
    return "Invalid File!"  # No file selected

#DrawChunks
def draw_chunks(current_number):
    global previous_number,surface_chunks
    if(previous_number != current_number):
        for i in range(previous_number,current_number):
            pygame.draw.rect(surface_chunks, (0,255,i/2.4,255), pygame.Rect(Script.chunkGridDicForPrinting[i][0]*HEIGHT_CHUNK+70,
                                                                            Script.chunkGridDicForPrinting[i][1]*HEIGHT_CHUNK-120, HEIGHT_CHUNK, HEIGHT_CHUNK))
        previous_number = current_number
    screen.blit(surface_chunks, (0,0))
    
#Button
def draw_button_SelectedFile(rect, text, color, text_color, transparency=128):
    # Rectangle
    pygame.draw.rect(screen, color, rect, width=1, border_radius=10)
    # Render the button text with the specified text color
    text_surf = pygame.font.Font(None, 20).render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    
def draw_button(rect, text, color, text_color, transparency=128):
    # Create a temporary surface for the button with an alpha channel
    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    # Fill the surface with the button color and transparency
    button_surface.fill((0,0,0,0))
    # Rectangle
    pygame.draw.rect(button_surface, (*color, transparency), button_surface.get_rect(), border_radius=10)
    # Blit the button surface onto the main screen
    screen.blit(button_surface, rect.topleft)
    # Rectangle
    pygame.draw.rect(screen, (255,255,255,255), rect, width=2, border_radius=10)
    
    # Render the button text with the specified text color
    text_surf = custom_font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_rectangle(rect, color, selected, question=False,question_hover=False, transparency=128):
    # Create a temporary surface for the button with an alpha channel
    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    # Fill the surface with the button color and transparency
    button_surface.fill((0,0,0,0))
    # Rectangle
    pygame.draw.rect(button_surface, (*color, transparency), button_surface.get_rect(), border_radius=10)
    # Blit the button surface onto the main screen
    screen.blit(button_surface, rect.topleft)
    #Center the image within the button rectangle
    if selected:
        image_rect = selected_button.get_rect(center=rect.center)
        screen.blit(selected_button, image_rect)
    if question:
        if question_hover:
            image_rect = question2_button.get_rect(center=rect.center)
            screen.blit(question2_button, image_rect)
        else:
            image_rect = question_button.get_rect(center=rect.center)
            screen.blit(question_button, image_rect)

def draw_loading_bar(rect, text, color, colorLoad, progress, maxP,transparency=128):
    # Create a temporary surface for the button with an alpha channel
    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    # Fill the surface with the button color and transparency
    button_surface.fill((0,0,0,0))
    # Rectangle
    pygame.draw.rect(button_surface, (*color, transparency), button_surface.get_rect(), border_radius=10)
    surfa = button_surface.get_rect()
    
    pygame.draw.rect(button_surface, (*colorLoad, 255),(surfa[0],surfa[1],surfa[2]*progress//maxP,surfa[3]) , border_radius=10)
    
    # Blit the button surface onto the main screen
    screen.blit(button_surface, rect.topleft)
    # Rectangle
    pygame.draw.rect(screen, (255,255,255,255), rect, width=2, border_radius=10)

    if colorLoad == (220,200,0):
        colorLoad = (255,255,0)
    else:
        colorLoad = (255,255,255)
    # Render the button text with the specified text color
    text_surf = custom_font.render(text, True,colorLoad )
    calcC = rect.center
    text_rect = text_surf.get_rect(center=(calcC[0],calcC[1]-30))
    screen.blit(text_surf, text_rect)

def draw_save_text(text):
    # Render the button text with the specified text color
    text_surf = custom_font.render(text, True,(255,255,0))
    text_rect = text_surf.get_rect(center=(WIDTH//2,500))
    screen.blit(text_surf, text_rect)

def draw_general_text(text,text2,text3):
    image_rect = upText_image.get_rect(center=(WIDTH//2,135))
    screen.blit(upText_image, image_rect)
    # Render the button text with the specified text color
    text_surf = custom_font.render(text, True,(255,255,255))
    text_rect = text_surf.get_rect(center=(WIDTH//2,110))
    screen.blit(text_surf, text_rect)
    text_surf = custom_font.render(text2, True,(255,255,255))
    text_rect = text_surf.get_rect(center=image_rect.center)
    screen.blit(text_surf, text_rect)
    text_surf = custom_font.render(text3, True,(255,255,255))
    text_rect = text_surf.get_rect(center=(WIDTH//2,160))
    screen.blit(text_surf, text_rect)

def draw_side_text(Title,text,text2,text3):
    CEN = WIDTH*2.9//4
    image_rect =descText_image.get_rect(center=(CEN,350))
    screen.blit(descText_image, image_rect)
    # Render the button text with the specified text color
    text_surf = custom_font.render(Title, True,(255,255,0))
    text_rect = text_surf.get_rect(center=(CEN,280))
    screen.blit(text_surf, text_rect)
    text_surf = custom_font.render(text, True,(255,255,255))
    text_rect = text_surf.get_rect(center=(CEN,310))
    screen.blit(text_surf, text_rect)
    text_surf = custom_font.render(text2, True,(255,255,255))
    text_rect = text_surf.get_rect(center=(CEN,335))
    screen.blit(text_surf, text_rect)
    text_surf = custom_font.render(text3, True,(255,255,255))
    text_rect = text_surf.get_rect(center=(CEN,360))
    screen.blit(text_surf, text_rect)

textDisplay = 0
# Fade parameters
fade_alpha = 0  # Start fully opaque (white)
fade_speed = 10    # Speed of the fade; higher is faster
# Main loop
clock = pygame.time.Clock()

fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill((255, 255, 255))

            
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if buttonFilePath_rect.collidepoint(event.pos) or (buttonFilePathBeg_rect.collidepoint(event.pos) and fadeIn):
                # Open the file dialog when button is clicked
                if(fade_alpha ==0):
                    selected_file_path = open_file_dialog(fadeIn)
            elif button1_rect.collidepoint(event.pos):
                ButtonBooleans[0] = not(ButtonBooleans[0])
            elif button2_rect.collidepoint(event.pos):
                ButtonBooleans[1] = not(ButtonBooleans[1])
            elif button3_rect.collidepoint(event.pos):
                ButtonBooleans[2] = not(ButtonBooleans[2])
            elif button4_rect.collidepoint(event.pos):
                ButtonBooleans[3] = not(ButtonBooleans[3])
            elif button1q_rect.collidepoint(event.pos):
                textDisplay = 1
            elif button2q_rect.collidepoint(event.pos):
                textDisplay = 2
            elif button3q_rect.collidepoint(event.pos):
                textDisplay = 3
            elif button4q_rect.collidepoint(event.pos):
                textDisplay = 4
            elif buttonConfirm_rect.collidepoint(event.pos):
                task_thread = threading.Thread(target=Script.process, args=(selected_file_path,ButtonBooleans[0],ButtonBooleans[1],ButtonBooleans[2],ButtonBooleans[3]))
                task_thread.start()
                fade_alpha = 1
    # Read the next frame from the video
    ret, frame = video.read()

    # If the video ends, reset it to the first frame
    if not ret:
        reset_video(video)
        ret, frame = video.read()

    frame = cv2.flip(frame, 1)

    # Resize and format the frame for Pygame
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.rotate(frame, -90)  # Rotate if needed

    # Draw the video frame as the background
    screen.blit(frame, (0, 0))

    if fadeIn == True:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(fade_surface, (0, 0))
        image_rect = upText_image.get_rect(center=(WIDTH//2,265))
        screen.blit(upText_image, image_rect)
        text_surf = custom_font.render("Select your Furrowfield Island File", True, (255,255,255))
        text_rect = text_surf.get_rect(center=(WIDTH//2,230))
        screen.blit(text_surf, text_rect)
        draw_button_SelectedFile(buttonFilePathBeg_rect, selected_file_path, button_color, (255,255,0) if buttonFilePathBeg_rect.collidepoint(mouse_pos) else (255,255,255))
        if selected_file_path!="Select file...":
            if fade_alpha != 255:
                fade_surface_new = pygame.Surface((WIDTH, HEIGHT))
                fade_surface_new.fill((255, 255, 255))
                fade_surface_new.set_alpha(fade_alpha)
            screen.blit(fade_surface_new, (0, 0))
            
            # Decrease alpha to fade out the overlay
            if fade_alpha < 255:
                fade_alpha += fade_speed
            else:
                fadeIn = False
                fade_speed = 5
# Implement the fade-in effect (For beggining)
    elif Script.RunningTask==False and fade_alpha > 0:
        # Create a white overlay with decreasing alpha
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((255, 255, 255))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
        
        # Decrease alpha to fade out the overlay
        fade_alpha -= fade_speed
        fade_alpha = max(fade_alpha, 0)  # Ensure it doesn't go below 0
    else:
        if fade_alpha > 0:
            # Create a white overlay with decreasing alpha
            if fade_alpha != 100:
                fade_surface = pygame.Surface((WIDTH, HEIGHT))
                fade_surface.fill((255, 255, 255))
                fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
            screen.blit(bg_image, (0, 0))
            
            # Decrease alpha to fade out the overlay
            if fade_alpha < 100:
                fade_alpha += fade_speed
        # Get the mouse position to handle hover effects
        mouse_pos = pygame.mouse.get_pos()
        if Script.RunningTask == False:
            draw_general_text(*TextBase)
            if textDisplay == 1:
                draw_side_text("> Transform the spoiled soil","Turn all spoiled soil into fertile soil,","and withered plants into healthy ones.","Rocks will have their moss removed too.")
            elif textDisplay == 2:
                draw_side_text("> Clean the filthy water","Destroy the filth of the island's waters.","All muddy water will turn to clear water.","All deadly water will become hot water.")
            elif textDisplay == 3:
                draw_side_text("> Repair the broken blocks","Replace all cracked or broken building","blocks with their unbroken conterparts.","Rubble will be destroyed as well.")
            elif textDisplay == 4:
                draw_side_text("> Old Deitree remains ","Destroy the corrupted blocks that are found","near the Old Deitree. Beware that some blocks","may have been used by Your builder friend...")
            # Draw buttons with hover effect
            draw_button(button1_rect, "> Transform the spoiled soil " if button1_rect.collidepoint(mouse_pos) else "  Transform the spoiled soil ",button_color,(255,255,0) if button1_rect.collidepoint(mouse_pos) else (255,255,255))
            draw_button(button2_rect, "> Clean the filthy water " if button2_rect.collidepoint(mouse_pos) else "  Clean the filthy water ", button_color, (255,255,0) if button2_rect.collidepoint(mouse_pos) else (255,255,255))
            draw_button(button3_rect, "> Repair the broken blocks " if button3_rect.collidepoint(mouse_pos) else "  Repair the broken blocks ", button_color, (255,255,0) if button3_rect.collidepoint(mouse_pos) else (255,255,255))
            draw_button(button4_rect, "> Old Deitree remains " if button4_rect.collidepoint(mouse_pos) else "  Old Deitree remains ", button_color, (255,255,0) if button4_rect.collidepoint(mouse_pos) else (255,255,255))

            draw_button_SelectedFile(buttonFilePath_rect, selected_file_path, button_color, (255,255,0) if buttonFilePath_rect.collidepoint(mouse_pos) else (255,255,255))

            draw_rectangle(button11_rect, button_color,ButtonBooleans[0])
            draw_rectangle(button22_rect, button_color,ButtonBooleans[1])
            draw_rectangle(button33_rect, button_color,ButtonBooleans[2])
            draw_rectangle(button44_rect, button_color,ButtonBooleans[3])

            draw_rectangle(button1q_rect, button_color,False,True,button1q_rect.collidepoint(mouse_pos))
            draw_rectangle(button2q_rect, button_color,False,True,button2q_rect.collidepoint(mouse_pos))
            draw_rectangle(button3q_rect, button_color,False,True,button3q_rect.collidepoint(mouse_pos))
            draw_rectangle(button4q_rect, button_color,False,True,button4q_rect.collidepoint(mouse_pos))

            draw_button(buttonConfirm_rect, "> Confirm " if buttonConfirm_rect.collidepoint(mouse_pos) else "  Confirm ", button_color, (255,255,0) if buttonConfirm_rect.collidepoint(mouse_pos) else (255,255,255))
        else:
            if ButtonBooleans[2]:
                draw_chunks(Script.BlockReading);
                draw_loading_bar(buttonLoading1_rect,"Reading chunk grid...",button_color,(220,200,0) if Script.ChunkReading != 0 and Script.ChunkReading != 8 else (200,200,200),Script.ChunkReading,8)
                draw_loading_bar(buttonLoading2_rect,"Destroying soiled items...", button_color,(220,200,0) if Script.ItemReading != 0 and Script.ItemReading != 200 else (200,200,200),Script.ItemReading,200)
                draw_loading_bar(buttonLoading3_rect,"Destroying ruins...", button_color,(220,200,0) if Script.ItemLocating != 0 and Script.ItemLocating != 200 else (200,200,200),Script.ItemLocating,200)
                draw_loading_bar(buttonLoading4_rect,"Destroying soiled blocks..."+ str(Script.BlockReading), button_color,(220,200,0) if Script.BlockReading != 0 and Script.BlockReading != 590 else (200,200,200),Script.BlockReading,590)
                draw_loading_bar(buttonLoading5_rect,"Mending ruins...", button_color,(220,200,0) if Script.ItemReplacing != 0 and Script.ItemReplacing != 5 else (200,200,200),Script.ItemReplacing,5)
                if Script.ItemReplacing == 5:
                    draw_save_text("Saving...")
                    TextBase = ["","File has been saved.","A backup can be found in the 'Backup' folder."]
            else:
                draw_loading_bar(buttonLoading3_rect,"Reading chunk grid...",button_color,(220,200,0) if Script.ChunkReading != 0 and Script.ChunkReading != 8 else (200,200,200),Script.ChunkReading,8)
                draw_loading_bar(buttonLoading4_rect,"Destroying soiled items...", button_color,(220,200,0) if Script.ItemReading != 0 and Script.ItemReading != 200 else (200,200,200),Script.ItemReading,200)
                draw_loading_bar(buttonLoading5_rect,"Destroying soiled blocks..."+ str(Script.BlockReading), button_color,(220,200,0) if Script.BlockReading != 0 and Script.BlockReading != 590 else (200,200,200),Script.BlockReading,590)
                if Script.BlockReading == 300 and Script.BlockReadingExtraThread == 590:
                    draw_save_text("Saving...")
                    TextBase = ["","File has been saved.","A backup can be found in the 'Backup' folder."]

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(30)

# Clean up
video.release()
pygame.quit()
sys.exit()
