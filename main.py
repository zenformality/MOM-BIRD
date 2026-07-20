import pygame
import random
import sys
import math
import asyncio

# -- Init ----------------------------------------------------------------------
async def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        print("Audio not available in this environment.")

    W, H = 480, 640
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Touch the Pipe If You Hate Your Mom")
    clock = pygame.time.Clock()

    # ----------------------------------------------------------------------------
    # --> CHANGE THESE TWO LINES TO YOUR FILE PATHS
    MOM_IMAGE_PATH  = "assets/mom.png"          # e.g. "C:/Users/Asus/Pictures/mom.png"
    SCARE_SOUND_PATH = "assets/scare.ogg"   # e.g. "C:/Users/Asus/Music/scare.ogg"
    # ----------------------------------------------------------------------------

    # -- Load assets (graceful fallback if files not found yet) --------------------
    mom_image = None
    scare_sound = None

    try:
        raw = pygame.image.load(MOM_IMAGE_PATH).convert_alpha()
        mom_image = pygame.transform.scale(raw, (W, H))
        print("Mom image loaded!")
    except Exception as e:
        print(f"Mom image not found ({e}) -- using placeholder drawing instead.")

    try:
        scare_sound = pygame.mixer.Sound(SCARE_SOUND_PATH)
        print("Jumpscare sound loaded!")
    except Exception as e:
        print(f"Jumpscare sound not found ({e}) -- will run silently.")

    sound_played = False   # so the sound only plays once per death

    # -- Colours -------------------------------------------------------------------
    SKY        = (112, 197, 255)
    GREEN      = (34,  177,  76)
    DARK_GREEN = (20,  120,  40)
    YELLOW     = (255, 220,  50)
    WHITE      = (255, 255, 255)
    BLACK      = (0,   0,    0)
    RED        = (220, 30,   30)
    ORANGE     = (255, 140,  0)
    SKIN       = (255, 210, 160)
    HAIR       = (60,  30,   10)
    GREY       = (180, 180, 180)

    # -- Fonts ---------------------------------------------------------------------
    try:
        font_big   = pygame.font.SysFont("Arial", 52, bold=True)
        font_mid   = pygame.font.SysFont("Arial", 32, bold=True)
        font_small = pygame.font.SysFont("Arial", 22)
    except Exception:
        font_big   = pygame.font.Font(None, 52)
        font_mid   = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 22)

    # -- Helper: draw text with outline --------------------------------------------
    def draw_text(surf, text, font, color, cx, cy, outline=BLACK):
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            s = font.render(text, True, outline)
            surf.blit(s, s.get_rect(center=(cx+dx, cy+dy)))
        s = font.render(text, True, color)
        surf.blit(s, s.get_rect(center=(cx, cy)))

    # -- Draw the bird -------------------------------------------------------------
    def draw_bird(surf, x, y, vel):
        angle = max(-30, min(30, -vel * 3))
        bird_surf = pygame.Surface((44, 34), pygame.SRCALPHA)
        pygame.draw.ellipse(bird_surf, YELLOW, (0, 5, 40, 24))
        wing_y = 14 + int(math.sin(pygame.time.get_ticks() / 100) * 4)
        pygame.draw.ellipse(bird_surf, ORANGE, (8, wing_y, 20, 10))
        pygame.draw.circle(bird_surf, WHITE, (30, 10), 6)
        pygame.draw.circle(bird_surf, BLACK, (32, 10), 3)
        pygame.draw.polygon(bird_surf, ORANGE, [(38, 12), (44, 15), (38, 18)])
        rotated = pygame.transform.rotate(bird_surf, angle)
        surf.blit(rotated, rotated.get_rect(center=(x, y)))

    # -- Draw a pipe ---------------------------------------------------------------
    def draw_pipe(surf, x, top_h, bot_y, pw=70):
        pygame.draw.rect(surf, GREEN,      (x, 0, pw, top_h))
        pygame.draw.rect(surf, DARK_GREEN, (x, 0, pw, top_h), 4)
        pygame.draw.rect(surf, GREEN,      (x-6, top_h-28, pw+12, 28))
        pygame.draw.rect(surf, DARK_GREEN, (x-6, top_h-28, pw+12, 28), 4)
        pygame.draw.rect(surf, GREEN,      (x, bot_y, pw, H - bot_y))
        pygame.draw.rect(surf, DARK_GREEN, (x, bot_y, pw, H - bot_y), 4)
        pygame.draw.rect(surf, GREEN,      (x-6, bot_y, pw+12, 28))
        pygame.draw.rect(surf, DARK_GREEN, (x-6, bot_y, pw+12, 28), 4)

    # -- Jumpscare: real image OR placeholder drawing -------------------------------
    def draw_jumpscare(surf, alpha_frac):
        """alpha_frac: 0.0 (invisible) -> 1.0 (fully shown)"""
        a = int(alpha_frac * 255)

        if mom_image:
            # -- Use the real mom image ------------------------------------------
            img = mom_image.copy()
            img.set_alpha(a)
            surf.blit(img, (0, 0))
        else:
            # -- Fallback placeholder drawing ------------------------------------
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            s.fill((120, 0, 0, min(a, 200)))
            pygame.draw.ellipse(s, (*SKIN, a), (W//2-110, 80, 220, 260))
            for bx, by, bw, bh in [
                (W//2-130,60,80,90),(W//2-70,40,90,80),
                (W//2+10,50,80,70),(W//2+70,70,70,80),
                (W//2-140,120,50,100),(W//2+110,110,50,120),
            ]:
                pygame.draw.ellipse(s, (*HAIR, a), (bx, by, bw, bh))
            pygame.draw.line(s, (*BLACK,a), (W//2-80,145),(W//2-30,165),8)
            pygame.draw.line(s, (*BLACK,a), (W//2+30,165),(W//2+80,145),8)
            pygame.draw.ellipse(s, (*WHITE,a), (W//2-75,160,50,38))
            pygame.draw.ellipse(s, (*WHITE,a), (W//2+25,160,50,38))
            pygame.draw.circle(s, (*BLACK,a), (W//2-50,179),14)
            pygame.draw.circle(s, (*BLACK,a), (W//2+50,179),14)
            pygame.draw.ellipse(s, (*BLACK,a), (W//2-55,255,110,60))
            for i in range(4):
                pygame.draw.rect(s, (*WHITE,a), (W//2-45+i*28, 255, 22, 22))
            surf.blit(s, (0, 0))

        # -- Overlay text (both modes) --------------------------------------------
        if alpha_frac > 0.6:
            txt_a = int((alpha_frac - 0.6) / 0.4 * 255)
            lines = ["YOU TOUCHED THE PIPE!", "HOW DARE YOU!!!", "DO YOU HATE YOUR MOM??"]
            for i, line in enumerate(lines):
                ts = font_mid.render(line, True, (255, 80, 80))
                ts.set_alpha(txt_a)
                surf.blit(ts, ts.get_rect(center=(W//2, 420 + i*44)))

    # -- Ground --------------------------------------------------------------------
    GROUND_Y = H - 60
    def draw_ground(surf, offset):
        pygame.draw.rect(surf, (210,170,80), (0, GROUND_Y, W, 60))
        pygame.draw.rect(surf, (140,100,40), (0, GROUND_Y, W, 6))
        for i in range(-1, W // 40 + 2):
            x = (i * 40 - offset % 40)
            pygame.draw.line(surf, (180,140,60), (x, GROUND_Y+6), (x+20, GROUND_Y+6), 2)

    # -- Clouds --------------------------------------------------------------------
    clouds = [(random.randint(0, W), random.randint(40, 200)) for _ in range(5)]
    def draw_clouds(surf, offset):
        for cx, cy in clouds:
            rx = (cx - offset * 0.3) % (W + 100) - 50
            for ox, oy, r in [(0,0,28),(20,0,32),(-20,0,22),(10,-15,20),(-10,-15,18)]:
                pygame.draw.circle(surf, WHITE, (int(rx+ox), cy+oy), r)

    # -- Constants -----------------------------------------------------------------
    GRAVITY   = 0.5
    JUMP_VEL  = -9
    PIPE_VEL  = 3
    PIPE_GAP  = 190
    PIPE_FREQ = 90
    PW        = 70
    BIRD_X    = 90

    # -- Game state ----------------------------------------------------------------
    def reset_game():
        nonlocal sound_played
        if scare_sound:
            scare_sound.stop()
        sound_played = False
        return {
            "bird_y"  : H // 2,
            "bird_vel": 0,
            "pipes"   : [],
            "score"   : 0,
            "offset"  : 0,
            "frame"   : 0,
            "state"   : "menu",   # menu | playing | jumpscare | dead
            "scare_t" : 0,
        }

    state = reset_game()

    # -- Main loop -----------------------------------------------------------------
    running = True
    while running:
        clock.tick(60)
        await asyncio.sleep(0)  # yield to event loop (required for pygbag)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if state["state"] == "menu":
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        state["state"] = "playing"
                elif state["state"] == "playing":
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        state["bird_vel"] = JUMP_VEL
                elif state["state"] == "dead":
                    if event.key in (pygame.K_SPACE, pygame.K_r):
                        state = reset_game()
                        state["state"] = "playing"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state["state"] == "playing":
                    state["bird_vel"] = JUMP_VEL
                elif state["state"] == "menu":
                    state["state"] = "playing"
                elif state["state"] == "dead":
                    state = reset_game()
                    state["state"] = "playing"

        # -- Update ----------------------------------------------------------------
        if state["state"] == "playing":
            state["frame"]  += 1
            state["offset"] += PIPE_VEL
            state["bird_vel"] += GRAVITY
            state["bird_y"]   += state["bird_vel"]

            # Spawn pipes (fixed range)
            if state["frame"] % PIPE_FREQ == 0:
                min_h = 80
                max_h = GROUND_Y - PIPE_GAP - 80
                if max_h <= min_h:
                    max_h = min_h + 10
                top_h = random.randint(min_h, max_h)
                bot_y = top_h + PIPE_GAP
                state["pipes"].append([W + 10, top_h, bot_y])

            # Move pipes & check collision
            new_pipes = []
            died = False
            for pipe in state["pipes"]:
                pipe[0] -= PIPE_VEL
                if pipe[0] + PW < BIRD_X and pipe[0] + PW + PIPE_VEL >= BIRD_X:
                    state["score"] += 1
                bx, by = BIRD_X, state["bird_y"]
                br = 15
                if bx + br > pipe[0] - 6 and bx - br < pipe[0] + PW + 6:
                    if by - br < pipe[1] or by + br > pipe[2]:
                        died = True
                if pipe[0] + PW > 0:
                    new_pipes.append(pipe)
            state["pipes"] = new_pipes

            if state["bird_y"] >= GROUND_Y - 15 or state["bird_y"] <= 0:
                died = True

            if died:
                state["state"]  = "jumpscare"
                state["scare_t"] = 0

        elif state["state"] == "jumpscare":
            state["scare_t"] += 1

            # Play sound exactly once at the start
            if state["scare_t"] == 1 and scare_sound and not sound_played:
                scare_sound.play()
                sound_played = True

            if state["scare_t"] > 150:   # ~2.5 seconds then go to dead screen
                state["state"] = "dead"

        # -- Draw ------------------------------------------------------------------
        screen.fill(SKY)
        draw_clouds(screen, state["offset"])

        for pipe in state["pipes"]:
            draw_pipe(screen, pipe[0], pipe[1], pipe[2])

        draw_ground(screen, state["offset"])

        if state["state"] not in ("jumpscare", "dead") or state["scare_t"] < 20:
            draw_bird(screen, BIRD_X, int(state["bird_y"]), state["bird_vel"])

        if state["state"] == "playing":
            draw_text(screen, str(state["score"]), font_big, WHITE, W//2, 60)

        # -- Overlays --------------------------------------------------------------
        if state["state"] == "menu":
            panel = pygame.Surface((360, 230), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 140))
            screen.blit(panel, (W//2-180, H//2-130))
            draw_text(screen, "Touch The Pipe", font_mid, YELLOW, W//2, H//2-90)
            draw_text(screen, "If You Hate Your Mom", font_small, WHITE, W//2, H//2-55)
            pygame.draw.line(screen, GREY, (W//2-130, H//2-35), (W//2+130, H//2-35), 2)
            draw_text(screen, "SPACE / Click to flap", font_small, WHITE, W//2, H//2+5)
            draw_text(screen, "Don't touch the pipe!", font_small, (255,180,180), W//2, H//2+40)
            draw_text(screen, "(your mom is watching)", font_small, ORANGE, W//2, H//2+70)

        elif state["state"] == "jumpscare":
            frac = min(state["scare_t"] / 30, 1.0)   # fast fade-in
            draw_jumpscare(screen, frac)

        elif state["state"] == "dead":
            draw_jumpscare(screen, 1.0)
            panel = pygame.Surface((340, 110), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 180))
            screen.blit(panel, (W//2-170, H-160))
            draw_text(screen, f"Score: {state['score']}", font_mid, YELLOW, W//2, H-130)
            draw_text(screen, "SPACE / R  to retry", font_small, WHITE, W//2, H-95)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())