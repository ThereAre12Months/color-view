#!/usr/bin/env python3

import os, sys
import json

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
from PIL import ImageGrab

def attempt_grab_screenshot():
    try:
        return ImageGrab.grab()
    except:
        return None

def pillow_to_pygame(img) -> pygame.Surface:
    return pygame.image.frombytes(
        img.tobytes(),
        img.size,
        img.mode,
    ).convert()

def resize_image(source, target_size):
    width_mul  = target_size[0] / source.get_width()
    height_mul = target_size[1] / source.get_height()
    mul = min(width_mul, height_mul)
    
    return pygame.transform.smoothscale_by(source, mul)

def rgb_to_hsv(color):
    Cmax  = max(*color)
    Cmin  = min(*color)
    delta = Cmax - Cmin

    if delta == 0:
        hue = 0 
    elif Cmax == color[0]:
        hue =  (color[1] - color[2]) / delta
        hue %= 6
    elif Cmax == color[1]:
        hue =  (color[2] - color[0]) / delta
        hue += 2
    elif Cmax == color[2]:
        hue =  (color[0] - color[1]) / delta
        hue += 4
    hue *= 60

    saturation = 0
    if Cmax:
        saturation = delta / Cmax
    saturation *= 100

    value = Cmax/255*100

    return hue, saturation, value

def get_closest_color_name(target_color):
    global COLORS, GRAYS

    hsv = rgb_to_hsv(target_color)
    if hsv[1] < 2:
        target_brightness = int(hsv[2] * 255 / 100)

        closest_color = None
        closest_dist  = float("inf")
        
        for color in GRAYS.values():
            dist = abs(target_brightness - color["brightness"])

            if dist < closest_dist:
                closest_color = color["name"]
                closest_dist  = dist

        return closest_color

    closest_color = None
    closest_dist  = float("inf")

    for color in COLORS.values():
        dist = (
            (color["rgb"][1] - target_color[1])**2 + \
            (color["rgb"][0] - target_color[0])**2 + \
            (color["rgb"][2] - target_color[2])**2
        )

        if dist < closest_dist:
            closest_color = color["name"]
            closest_dist  = dist

    return closest_color

def draw_drop_request(dp, font):
    surf = font.render("Please drop an image here", True, (255, 255, 255))
    dp.blit(surf, surf.get_rect(center = (dp.get_width()//2, dp.get_height()//2)))

def draw_tooltip(dp, font, color, pos):
    hsv = rgb_to_hsv(color)

    lines = (
        ("rgb: ", ", ".join(map(str, color))),
        ("hex: ", f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"),
        ("hsv: ", f"{hsv[0]:.0f}° {hsv[1]:.0f}% {hsv[2]:.0f}%"),
        ("name: ", get_closest_color_name(color)),
    )

    tooltip_width  = 0
    tooltip_height = 0
    
    lines_rendered = []
    for line in lines:
        left  = font.render(line[0], True, (255, 255, 255))
        right = font.render(line[1], True, (255, 255, 255))
        lines_rendered.append((left, right))

        line_width  = left.get_width()+right.get_width()
        line_height = max(left.get_height(), right.get_height())
        
        if line_width > tooltip_width:
            tooltip_width = line_width
        tooltip_height += line_height

    # margins
    tooltip_width  += 20 
    tooltip_height += 20

    tooltip_surf = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
    tooltip_surf.fill((0,0,0,0))
    pygame.draw.rect(tooltip_surf, (0,0,0), (0,0,tooltip_width,tooltip_height), border_radius=10)
    
    current_height = 10
    for line in lines_rendered:
        tooltip_surf.blit(line[0], (10, current_height))
        tooltip_surf.blit(line[1], line[1].get_rect(topright = (tooltip_width-10, current_height)))
        current_height += max(line[0].get_height(), line[1].get_height())

    if (pos[0]+tooltip_width+10) < dp.get_width():
        if (pos[1]+tooltip_height+10) < dp.get_height():
            dp.blit(tooltip_surf, (pos[0]+10, pos[1]+10))
        else:
            dp.blit(tooltip_surf, tooltip_surf.get_rect(bottomleft = (pos[0]+10, pos[1]+10)))
    else:
        if (pos[1]+tooltip_height+10) < dp.get_height():
            dp.blit(tooltip_surf, tooltip_surf.get_rect(topright = (pos[0]-10, pos[1]+10)))
        else:
            dp.blit(tooltip_surf, tooltip_surf.get_rect(bottomright = (pos[0]-10, pos[1]+10)))
    
def screen_to_image_space(pos, screen_size, image_size):
    width_mul  = screen_size[0] / image_size[0]
    height_mul = screen_size[1] / image_size[1]
    mul = min(width_mul, height_mul)

    x_offset = (screen_size[0] - image_size[0]*mul) // 2

    x = (pos[0] - x_offset) / mul
    y =  pos[1] / mul

    return int(x), int(y)

def main():
    global COLORS, GRAYS

    with open("colors.json") as f:
        COLORS = json.load(f)
    with open("grays.json") as f:
        GRAYS  = json.load(f)

    loaded_img = attempt_grab_screenshot()

    pygame.init()
    app = pygame.display.set_mode(
        (0,0),
        (pygame.FULLSCREEN*bool(loaded_img)) | pygame.RESIZABLE,
        vsync = 1,
    )
    pygame.display.set_caption("")
    pygame.display.set_icon(pygame.Surface((0,0)))
    font = pygame.font.SysFont(None, 30)
    
    if loaded_img:
        loaded_img = pillow_to_pygame(loaded_img)

        resized_img = resize_image(loaded_img, app.get_size())
        x_offset = (app.get_width() - resized_img.get_width()) // 2

    W,H = app.get_size()
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
                break

            if ev.type == pygame.DROPFILE:
                loaded_img  = pygame.image.load(ev.file).convert()
                resized_img = resize_image(loaded_img, (W,H))

            if loaded_img:
                if ev.type == pygame.VIDEORESIZE:
                    W,H = ev.size
                    resized_img = resize_image(loaded_img, (W,H))

                if ev.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                    break

        if not running:
            break

        app.fill((0,0,0))
        if not loaded_img:
            draw_drop_request(app, font)
        else:
            app.blit(resized_img, resized_img.get_rect(midtop=(W//2, 0)))
            mx, my = screen_to_image_space(pygame.mouse.get_pos(), (W,H), loaded_img.get_size())

            if mx in range(0, loaded_img.get_width()) and \
               my in range(0, loaded_img.get_height()):
                source_color = loaded_img.get_at((mx, my))[:3]
                draw_tooltip(app, font, source_color, (mx,my))

        pygame.display.flip()

    pygame.quit()
    
if __name__ == "__main__":
    main()
