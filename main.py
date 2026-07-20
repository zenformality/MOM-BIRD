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
    MOM_IMAGE_PATH  = "assets/mom.png"
    SCARE_SOUND_PATH = "assets/scare.ogg"
    # ----------------------------------------------------------------------------

    # -- Load assets (graceful fallback) ------------------------------------------
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

    sound_played = False

    # -- Colours -------------------------------------------------------------------
    BLACK      = (0,     0,    0)
    WHITE      = (255, 255, 255)
    YELLOW     = (255, 220,  50)
    RED        = (220,  30,  30)
    ORANGE     = (255, 140,   0)
    SKIN       = (255, 210, 160)
    HAIR       = (60,   30,  10)
    GREY       = (180, 180, 180)

    # -- Pre-render gradient sky --------------------------------------------------
    sky_surf = pygame.Surface((W, H))
    sky_top    = (70, 160, 240)
    sky_mid    = (135, 206, 250)
    sky_bottom = (200, 230, 255)
    for y in range(H):
        t = y / H
        if t < 0.5:
            f = t / 0.5
        else:
            f = 1.0
        r = int(sky_top[0] + (sky_mid[0] - sky_top[0]) * f)
        g = int(sky_top[1] + (sky_mid[1] - sky_top[1]) * f)
        b = int(sky_top[2] + (sky_mid[2] - sky_top[2]) * f)
        if t >= 0.5:
            f2 = (t - 0.5) / 0.5
            r = int(r + (sky_bottom[0] - r) * f2)
            g = int(g + (sky_bottom[1] - g) * f2)
            b = int(b + (sky_bottom[2] - b) * f2)
        pygame.draw.line(sky_surf, (r, g, b), (0, y), (W, y))

    # -- Pipe width ---------------------------------------------------------------
    PW = 72

    # -- Pre-render ground strip --------------------------------------------------
    GROUND_Y = H - 60
    ground_surf = pygame.Surface((W + 80, 60))
    # Dirt layers
    ground_surf.fill((194, 150, 70))
    for y in range(60):
        t = y / 60
        r = int(194 - 40 * t)
        g = int(150 - 50 * t)
        b = int(70 - 20 * t)
        pygame.draw.line(ground_surf, (max(r, 0), max(g, 0), max(b, 0)), (0, y), (W + 80, y))
    # Grass top
    pygame.draw.rect(ground_surf, (80, 180, 50), (0, 0, W + 80, 8))
    pygame.draw.rect(ground_surf, (60, 150, 35), (0, 8, W + 80, 3))
    # Grass blades
    random.seed(42)
    for i in range(60):
        gx = random.randint(0, W + 80)
        gh = random.randint(4, 12)
        gc = random.choice([(90, 200, 60), (70, 170, 45), (100, 210, 70), (60, 160, 40)])
        pygame.draw.line(ground_surf, gc, (gx, 0), (gx + random.randint(-3, 3), -gh), 2)
    random.seed()

    # -- Fonts -------------------------------------------------------------------
    try:
        font_big    = pygame.font.SysFont("Arial", 56, bold=True)
        font_mid    = pygame.font.SysFont("Arial", 34, bold=True)
        font_small  = pygame.font.SysFont("Arial", 22)
        font_title  = pygame.font.SysFont("Arial", 42, bold=True)
    except Exception:
        font_big    = pygame.font.Font(None, 56)
        font_mid    = pygame.font.Font(None, 34)
        font_small  = pygame.font.Font(None, 22)
        font_title  = pygame.font.Font(None, 42)

    # -- Helper: draw text with outline -------------------------------------------
    def draw_text(surf, text, font, color, cx, cy, outline=(0, 0, 0), outline_w=2):
        for dx in range(-outline_w, outline_w + 1):
            for dy in range(-outline_w, outline_w + 1):
                if dx * dx + dy * dy <= outline_w * outline_w + 1:
                    s = font.render(text, True, outline)
                    surf.blit(s, s.get_rect(center=(cx + dx, cy + dy)))
        s = font.render(text, True, color)
        surf.blit(s, s.get_rect(center=(cx, cy)))

    def draw_text_shadow(surf, text, font, color, cx, cy, shadow_color=(0, 0, 0, 120)):
        """Draw text with a soft drop shadow."""
        shadow = font.render(text, True, (40, 40, 40))
        shadow.set_alpha(100)
        surf.blit(shadow, shadow.get_rect(center=(cx + 3, cy + 3)))
        s = font.render(text, True, color)
        surf.blit(s, s.get_rect(center=(cx, cy)))

    # -- Draw the bird (detailed) -------------------------------------------------
    def draw_bird(surf, x, y, vel):
        angle = max(-35, min(35, -vel * 3.5))
        bw, bh = 52, 40
        bird_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)

        # Body gradient (yellow to orange-ish)
        for row in range(bh):
            t = row / bh
            r = int(255 - 15 * t)
            g = int(220 - 40 * t)
            b = int(50 + 10 * t)
            # Ellipse mask
            cx_e, cy_e = bw // 2, bh // 2 + 2
            rx_e, ry_e = 22, 14
            for col in range(bw):
                dx = (col - cx_e) / rx_e
                dy = (row - cy_e) / ry_e
                if dx * dx + dy * dy <= 1.0:
                    bird_surf.set_at((col, row), (r, g, b))

        # Belly (lighter oval)
        belly_surf = pygame.Surface((28, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(belly_surf, (255, 245, 180, 200), (0, 0, 28, 16))
        bird_surf.blit(belly_surf, (10, 16))

        # Wing with animation
        wing_y_offset = int(math.sin(pygame.time.get_ticks() / 80) * 6)
        wing_surf = pygame.Surface((22, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(wing_surf, (230, 170, 30), (0, 0, 22, 12))
        pygame.draw.ellipse(wing_surf, (200, 140, 20), (0, 0, 22, 12), 1)
        bird_surf.blit(wing_surf, (6, 10 + wing_y_offset))

        # Eye white
        pygame.draw.circle(bird_surf, (255, 255, 255), (36, 11), 8)
        pygame.draw.circle(bird_surf, (200, 200, 200), (36, 11), 8, 1)
        # Pupil
        pygame.draw.circle(bird_surf, (10, 10, 10), (38, 10), 4)
        # Eye highlight
        pygame.draw.circle(bird_surf, (255, 255, 255), (40, 8), 2)

        # Beak
        beak_pts = [(42, 13), (50, 16), (42, 20)]
        pygame.draw.polygon(bird_surf, (255, 160, 30), beak_pts)
        pygame.draw.polygon(bird_surf, (200, 120, 20), beak_pts, 1)
        # Beak line
        pygame.draw.line(bird_surf, (180, 100, 10), (42, 16), (49, 16), 1)

        # Eyebrow (angry look)
        pygame.draw.line(bird_surf, (80, 50, 10), (30, 4), (38, 6), 2)

        rotated = pygame.transform.rotate(bird_surf, angle)
        surf.blit(rotated, rotated.get_rect(center=(x, y)))

    # -- Draw a pipe (3D shaded) --------------------------------------------------
    def pipe_rect(surf, rx, ry, rw, rh):
        """Draw a pipe body segment with horizontal gradient shading."""
        for px in range(rw):
            t = px / rw
            highlight = max(0, 1.0 - abs(t - 0.28) / 0.28)
            shadow   = max(0, (t - 0.72) / 0.28)
            r = max(0, min(255, int(34 + 35 * highlight - 20 * shadow)))
            g = max(0, min(255, int(177 + 35 * highlight - 40 * shadow)))
            b = max(0, min(255, int(76 + 25 * highlight - 20 * shadow)))
            pygame.draw.line(surf, (r, g, b), (rx + px, ry), (rx + px, ry + rh))
        # Highlight stripe
        pygame.draw.line(surf, (100, 220, 120), (rx + int(rw * 0.28), ry),
                         (rx + int(rw * 0.28), ry + rh), 3)
        # Dark right edge
        pygame.draw.line(surf, (15, 80, 30), (rx + rw - 2, ry), (rx + rw - 2, ry + rh), 2)
        # Border
        pygame.draw.rect(surf, (15, 80, 30), (rx, ry, rw, rh), 2)

    def pipe_cap(surf, rx, ry, rw, rh):
        """Draw a pipe cap (the wider lip) with shading."""
        for px in range(rw):
            t = px / rw
            highlight = max(0, 1.0 - abs(t - 0.28) / 0.28)
            shadow   = max(0, (t - 0.72) / 0.28)
            r = max(0, min(255, int(34 + 40 * highlight - 20 * shadow)))
            g = max(0, min(255, int(177 + 40 * highlight - 40 * shadow)))
            b = max(0, min(255, int(76 + 30 * highlight - 20 * shadow)))
            pygame.draw.line(surf, (r, g, b), (rx + px, ry), (rx + px, ry + rh))
        # Top highlight
        pygame.draw.line(surf, (120, 230, 140), (rx + 2, ry + 1), (rx + rw - 3, ry + 1), 2)
        # Bottom shadow
        pygame.draw.line(surf, (15, 80, 30), (rx + 2, ry + rh - 2), (rx + rw - 3, ry + rh - 2), 2)
        # Highlight stripe
        pygame.draw.line(surf, (100, 220, 120), (rx + int(rw * 0.28), ry + 2),
                         (rx + int(rw * 0.28), ry + rh - 2), 3)
        # Border
        pygame.draw.rect(surf, (15, 80, 30), (rx, ry, rw, rh), 2)

    def draw_pipe(surf, x, top_h, bot_y):
        cap_w = PW + 14
        cap_h = 28
        cap_x = int(x - 7)

        # --- Top pipe ---
        if top_h > cap_h:
            pipe_rect(surf, int(x), 0, PW, top_h - cap_h)
        pipe_cap(surf, cap_x, top_h - cap_h, cap_w, cap_h)

        # --- Bottom pipe ---
        pipe_cap(surf, cap_x, bot_y, cap_w, cap_h)
        if H - bot_y - cap_h > 0:
            pipe_rect(surf, int(x), bot_y + cap_h, PW, H - bot_y - cap_h)

    # -- Draw clouds (fluffy, semi-transparent) -----------------------------------
    clouds = []
    for _ in range(7):
        cx = random.randint(-50, W + 50)
        cy = random.randint(30, 180)
        size = random.uniform(0.7, 1.4)
        speed = random.uniform(0.15, 0.4)
        alpha = random.randint(160, 220)
        clouds.append((cx, cy, size, speed, alpha))

    def draw_cloud(surf, cx, cy, size, alpha):
        cs = pygame.Surface((120, 60), pygame.SRCALPHA)
        color = (255, 255, 255, alpha)
        parts = [
            (0, 20, 24), (20, 10, 30), (45, 5, 34), (70, 10, 28),
            (90, 18, 22), (10, 30, 20), (50, 28, 24), (35, 15, 26),
        ]
        for ox, oy, r in parts:
            r = int(r * size)
            pygame.draw.circle(cs, color, (int(ox * size), int(oy * size)), r)
        surf.blit(cs, (int(cx - 50 * size), int(cy - 20 * size)))

    def draw_clouds(surf, offset):
        for cx, cy, size, speed, alpha in clouds:
            rx = (cx - offset * speed) % (W + 160) - 80
            draw_cloud(surf, rx, cy, size, alpha)

    # -- Draw ground with parallax ------------------------------------------------
    def draw_ground(surf, offset):
        gx = -(int(offset) % 80)
        surf.blit(ground_surf, (gx, GROUND_Y))

    # -- Draw vignette effect (for death) ----------------------------------------
    vignette_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(80):
        a = int(180 * (i / 80) ** 1.5)
        r_inner = int((W + H) * 0.5 * (1 - i / 80))
        pygame.draw.rect(vignette_surf, (0, 0, 0, a), (0, 0, W, H), max(1, int((W + H) * 0.04)))
    # Simpler approach: corner darkening
    vignette_surf.fill((0, 0, 0, 0))
    for corner_x, corner_y in [(0, 0), (W, 0), (0, H), (W, H)]:
        for i in range(120, 0, -1):
            a = int(60 * (1 - i / 120))
            pygame.draw.circle(vignette_surf, (0, 0, 0, a), (corner_x, corner_y), i * 3)

    # -- Score panel (pre-render) -------------------------------------------------
    score_panel_w, score_panel_h = 120, 55
    score_panel = pygame.Surface((score_panel_w, score_panel_h), pygame.SRCALPHA)
    # Rounded rect approximation
    pygame.draw.rect(score_panel, (0, 0, 0, 100), (0, 0, score_panel_w, score_panel_h), border_radius=12)
    pygame.draw.rect(score_panel, (255, 255, 255, 40), (0, 0, score_panel_w, score_panel_h), 2, border_radius=12)

    # -- Menu panel (pre-render) --------------------------------------------------
    menu_w, menu_h = 380, 280
    menu_panel = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
    # Dark gradient panel
    for row in range(menu_h):
        t = row / menu_h
        a = int(160 + 40 * t)
        pygame.draw.line(menu_panel, (20, 20, 40, a), (0, row), (menu_w, row))
    # Border with rounded feel
    pygame.draw.rect(menu_panel, (255, 220, 50, 180), (0, 0, menu_w, menu_h), 3, border_radius=16)
    # Inner glow
    pygame.draw.rect(menu_panel, (255, 220, 50, 30), (4, 4, menu_w - 8, menu_h - 8), 1, border_radius=14)

    # -- Dead panel (pre-render) --------------------------------------------------
    dead_w, dead_h = 360, 140
    dead_panel = pygame.Surface((dead_w, dead_h), pygame.SRCALPHA)
    for row in range(dead_h):
        t = row / dead_h
        a = int(190 + 40 * t)
        pygame.draw.line(dead_panel, (30, 0, 0, a), (0, row), (dead_w, row))
    pygame.draw.rect(dead_panel, (220, 50, 50, 200), (0, 0, dead_w, dead_h), 3, border_radius=12)

    # -- Particles ----------------------------------------------------------------
    particles = []

    def spawn_feathers(x, y, count=5):
        """Soft feathers that drift down when bird flaps."""
        for _ in range(count):
            angle = random.uniform(-0.8, 0.8)  # mostly sideways
            speed = random.uniform(0.5, 2.5)
            life = random.randint(35, 55)
            particles.append({
                "type": "feather",
                "x": x + random.randint(-5, 5),
                "y": y + random.randint(-3, 3),
                "vx": math.cos(angle) * speed + random.uniform(-0.3, 0.3),
                "vy": random.uniform(-1.5, -0.3),
                "life": life, "max_life": life,
                "color": random.choice([(255, 240, 160), (255, 220, 120), (255, 200, 80)]),
                "size": random.uniform(3, 6),
                "rot": random.uniform(0, 360),
                "rot_speed": random.uniform(-8, 8),
                "wobble": random.uniform(0, math.pi * 2),
            })

    def spawn_sparkles(x, y, count=8):
        """Golden sparkles when scoring a point."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 4.5)
            life = random.randint(25, 45)
            particles.append({
                "type": "sparkle",
                "x": x, "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 1.5,
                "life": life, "max_life": life,
                "color": random.choice([(255, 255, 100), (255, 230, 50), (255, 200, 0)]),
                "size": random.uniform(2, 5),
                "rot": random.uniform(0, 360),
                "rot_speed": random.uniform(-12, 12),
            })

    def spawn_fire(x, y, count=12):
        """Fiery embers + smoke on death."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            life = random.randint(30, 55)
            particles.append({
                "type": "fire",
                "x": x + random.randint(-8, 8),
                "y": y + random.randint(-8, 8),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 3,
                "life": life, "max_life": life,
                "color": random.choice([(255, 120, 30), (255, 80, 20), (255, 200, 50)]),
                "size": random.uniform(3, 7),
                "glow": True,
            })
        # Smoke puffs
        for _ in range(count // 2):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2)
            life = random.randint(40, 70)
            particles.append({
                "type": "smoke",
                "x": x + random.randint(-5, 5),
                "y": y + random.randint(-5, 5),
                "vx": math.cos(angle) * speed,
                "vy": random.uniform(-2.5, -0.8),
                "life": life, "max_life": life,
                "color": (120, 120, 120),
                "size": random.uniform(4, 8),
            })

    def spawn_particles(x, y, count=8, color=(255, 220, 50)):
        """Generic fallback — just sparkles."""
        spawn_sparkles(x, y, count)

    def update_particles():
        alive = []
        for p in particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            t = 1 - p["life"] / p["max_life"]  # 0→1 over lifetime
            if p["type"] == "feather":
                p["vy"] += 0.04           # gentle gravity
                p["vx"] *= 0.99           # air drag
                p["wobble"] += 0.15
                p["vx"] += math.sin(p["wobble"]) * 0.15
                p["rot"] += p["rot_speed"]
                p["size"] *= 0.997        # shrink slowly
            elif p["type"] == "sparkle":
                p["vy"] += 0.06
                p["vx"] *= 0.97
                p["rot"] += p["rot_speed"]
                p["size"] *= 0.985
            elif p["type"] == "fire":
                p["vy"] -= 0.05          # rises
                p["vx"] *= 0.96
                p["size"] *= 0.98
                # Shift color toward orange/red as it ages
                r, g, b = p["color"]
                p["color"] = (min(255, r + 1), max(0, g - 3), max(0, b - 2))
            elif p["type"] == "smoke":
                p["vy"] -= 0.02
                p["vx"] *= 0.95
                p["size"] += 0.15         # expands
            if p["life"] > 0 and p["size"] > 0.3:
                alive.append(p)
        particles.clear()
        particles.extend(alive)

    def draw_star(surf, cx, cy, r_outer, r_inner, color, rot_deg, alpha):
        """Draw a 4-pointed star."""
        pts = []
        for i in range(8):
            a = math.radians(rot_deg + i * 45)
            r = r_outer if i % 2 == 0 else r_inner
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        s = pygame.Surface((int(r_outer * 2 + 4), int(r_outer * 2 + 4)), pygame.SRCALPHA)
        ox, oy = r_outer + 2, r_outer + 2
        shifted = [(px + ox, py + oy) for px, py in pts]
        pygame.draw.polygon(s, (*color, alpha), shifted)
        surf.blit(s, (int(cx - r_outer - 2), int(cy - r_outer - 2)))

    def draw_particles(surf):
        for p in particles:
            life_frac = p["life"] / p["max_life"]
            alpha = int(255 * life_frac)
            r, g, b = p["color"]
            px, py = int(p["x"]), int(p["y"])

            if p["type"] == "feather":
                # Small elongated shape, rotated
                fw, fh = int(p["size"] * 1.8), int(p["size"])
                fs = pygame.Surface((fw * 2, fh * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(fs, (r, g, b, alpha), (fw - fw, fh - fh, fw * 2, fh * 2))
                # Center line
                pygame.draw.line(fs, (r - 30, g - 30, b - 20, alpha),
                                 (2, fh), (fw * 2 - 2, fh), 1)
                rotated = pygame.transform.rotate(fs, p["rot"])
                rect = rotated.get_rect(center=(px, py))
                surf.blit(rotated, rect)

            elif p["type"] == "sparkle":
                size = max(1, int(p["size"]))
                # Glow behind
                gs = size + 3
                glow = pygame.Surface((gs * 2, gs * 2), pygame.SRCALPHA)
                glow_a = int(alpha * 0.4)
                pygame.draw.circle(glow, (r, g, b, glow_a), (gs, gs), gs)
                surf.blit(glow, (px - gs, py - gs))
                # Star shape
                draw_star(surf, px, py, size, size * 0.4, (r, g, b),
                          p.get("rot", 0), alpha)

            elif p["type"] == "fire":
                size = max(1, int(p["size"]))
                # Outer glow
                gs = size + 6
                glow = pygame.Surface((gs * 2, gs * 2), pygame.SRCALPHA)
                glow_a = int(alpha * 0.35)
                pygame.draw.circle(glow, (255, 100, 20, glow_a), (gs, gs), gs)
                surf.blit(glow, (px - gs, py - gs))
                # Core
                core = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(core, (r, g, b, alpha), (size, size), size)
                # Hot center
                hot_a = int(alpha * 0.7)
                pygame.draw.circle(core, (255, 255, 180, hot_a),
                                   (size, size), max(1, size // 2))
                surf.blit(core, (px - size, py - size))

            elif p["type"] == "smoke":
                size = max(1, int(p["size"]))
                a = int(alpha * 0.5)  # more transparent
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (r, g, b, a), (size, size), size)
                surf.blit(s, (px - size, py - size))

    # -- Jumpscare ---------------------------------------------------------------
    def draw_jumpscare(surf, alpha_frac):
        a = int(alpha_frac * 255)
        if mom_image:
            img = mom_image.copy()
            img.set_alpha(a)
            surf.blit(img, (0, 0))
        else:
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            s.fill((120, 0, 0, min(a, 200)))
            pygame.draw.ellipse(s, (*SKIN, a), (W // 2 - 110, 80, 220, 260))
            for bx, by, bw, bh in [
                (W // 2 - 130, 60, 80, 90), (W // 2 - 70, 40, 90, 80),
                (W // 2 + 10, 50, 80, 70), (W // 2 + 70, 70, 70, 80),
                (W // 2 - 140, 120, 50, 100), (W // 2 + 110, 110, 50, 120),
            ]:
                pygame.draw.ellipse(s, (*HAIR, a), (bx, by, bw, bh))
            pygame.draw.line(s, (*BLACK, a), (W // 2 - 80, 145), (W // 2 - 30, 165), 8)
            pygame.draw.line(s, (*BLACK, a), (W // 2 + 30, 165), (W // 2 + 80, 145), 8)
            pygame.draw.ellipse(s, (*WHITE, a), (W // 2 - 75, 160, 50, 38))
            pygame.draw.ellipse(s, (*WHITE, a), (W // 2 + 25, 160, 50, 38))
            pygame.draw.circle(s, (*BLACK, a), (W // 2 - 50, 179), 14)
            pygame.draw.circle(s, (*BLACK, a), (W // 2 + 50, 179), 14)
            pygame.draw.ellipse(s, (*BLACK, a), (W // 2 - 55, 255, 110, 60))
            for i in range(4):
                pygame.draw.rect(s, (*WHITE, a), (W // 2 - 45 + i * 28, 255, 22, 22))
            surf.blit(s, (0, 0))
        if alpha_frac > 0.6:
            txt_a = int((alpha_frac - 0.6) / 0.4 * 255)
            lines = ["YOU TOUCHED THE PIPE!", "HOW DARE YOU!!!", "DO YOU HATE YOUR MOM??"]
            for i, line in enumerate(lines):
                ts = font_mid.render(line, True, (255, 80, 80))
                ts.set_alpha(txt_a)
                surf.blit(ts, ts.get_rect(center=(W // 2, 420 + i * 44)))

    # -- Constants ----------------------------------------------------------------
    GRAVITY   = 0.5
    JUMP_VEL  = -9
    PIPE_VEL  = 3
    PIPE_GAP  = 185
    PIPE_FREQ = 90
    BIRD_X    = 90

    # -- Game state ---------------------------------------------------------------
    def reset_game():
        nonlocal sound_played
        if scare_sound:
            scare_sound.stop()
        sound_played = False
        particles.clear()
        return {
            "bird_y"  : H // 2,
            "bird_vel": 0,
            "pipes"   : [],
            "score"   : 0,
            "offset"  : 0,
            "frame"   : 0,
            "state"   : "menu",
            "scare_t" : 0,
            "shake"   : 0,
        }

    state = reset_game()

    # -- Main loop ----------------------------------------------------------------
    running = True
    while running:
        clock.tick(60)
        await asyncio.sleep(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if state["state"] == "menu":
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        state["state"] = "playing"
                        spawn_feathers(BIRD_X, state["bird_y"], 5)
                elif state["state"] == "playing":
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        state["bird_vel"] = JUMP_VEL
                        spawn_feathers(BIRD_X, state["bird_y"] + 5, 4)
                elif state["state"] == "dead":
                    if event.key in (pygame.K_SPACE, pygame.K_r):
                        state = reset_game()
                        state["state"] = "playing"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state["state"] == "playing":
                    state["bird_vel"] = JUMP_VEL
                    spawn_feathers(BIRD_X, state["bird_y"] + 5, 4)
                elif state["state"] == "menu":
                    state["state"] = "playing"
                    spawn_feathers(BIRD_X, state["bird_y"], 5)
                elif state["state"] == "dead":
                    state = reset_game()
                    state["state"] = "playing"

        # -- Update ----------------------------------------------------------------
        if state["state"] == "playing":
            state["frame"]  += 1
            state["offset"] += PIPE_VEL
            state["bird_vel"] += GRAVITY
            state["bird_y"]   += state["bird_vel"]

            # Spawn pipes
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
                    spawn_sparkles(BIRD_X + 10, state["bird_y"], 8)
                bx, by = BIRD_X, state["bird_y"]
                br = 15
                if bx + br > pipe[0] - 7 and bx - br < pipe[0] + PW + 7:
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
                state["shake"] = 12
                spawn_fire(BIRD_X, state["bird_y"], 15)

        elif state["state"] == "jumpscare":
            state["scare_t"] += 1
            if state["shake"] > 0:
                state["shake"] -= 1

            if state["scare_t"] == 1 and scare_sound and not sound_played:
                scare_sound.play()
                sound_played = True

            if state["scare_t"] > 150:
                state["state"] = "dead"

        elif state["state"] == "dead":
            if state["shake"] > 0:
                state["shake"] -= 1

        update_particles()

        # -- Draw ------------------------------------------------------------------
        # Screen shake offset
        sx, sy = 0, 0
        if state["shake"] > 0:
            sx = random.randint(-state["shake"], state["shake"])
            sy = random.randint(-state["shake"], state["shake"])

        # Sky gradient
        screen.blit(sky_surf, (sx, sy))

        # Clouds
        draw_clouds(screen, state["offset"])

        # Pipes
        for pipe in state["pipes"]:
            draw_pipe(screen, pipe[0] + sx, pipe[1], pipe[2])

        # Ground
        draw_ground(screen, state["offset"])

        # Bird (hide during mid-jumpscare)
        if state["state"] not in ("jumpscare", "dead") or state["scare_t"] < 20:
            draw_bird(screen, BIRD_X + sx, int(state["bird_y"]) + sy, state["bird_vel"])

        # Particles (behind UI)
        draw_particles(screen)

        # -- Score (during playing) ------------------------------------------------
        if state["state"] == "playing":
            sp_x = W // 2 - score_panel_w // 2 + sx
            sp_y = 20 + sy
            screen.blit(score_panel, (sp_x, sp_y))
            draw_text_shadow(screen, str(state["score"]), font_big, (255, 255, 255),
                             W // 2 + sx, 48 + sy)

        # -- Overlays --------------------------------------------------------------
        if state["state"] == "menu":
            mp_x = W // 2 - menu_w // 2
            mp_y = H // 2 - menu_h // 2
            screen.blit(menu_panel, (mp_x, mp_y))

            # Decorative bird icon on menu
            draw_bird(screen, W // 2, mp_y + 55, -2)

            draw_text(screen, "Touch The Pipe", font_title, (255, 230, 80), W // 2, mp_y + 100)
            draw_text(screen, "If You Hate Your Mom", font_small, (200, 200, 220), W // 2, mp_y + 135)

            # Divider
            pygame.draw.line(screen, (255, 220, 50, 150), (mp_x + 30, mp_y + 155),
                             (mp_x + menu_w - 30, mp_y + 155), 2)

            draw_text(screen, "SPACE / Click to flap", font_small, (200, 220, 255), W // 2, mp_y + 185)
            draw_text(screen, "Don't touch the pipe!", font_small, (255, 150, 150), W // 2, mp_y + 215)
            draw_text(screen, "(your mom is watching)", font_small, (255, 180, 80), W // 2, mp_y + 250)

        elif state["state"] == "jumpscare":
            frac = min(state["scare_t"] / 30, 1.0)
            draw_jumpscare(screen, frac)

        elif state["state"] == "dead":
            draw_jumpscare(screen, 1.0)
            screen.blit(vignette_surf, (0, 0))

            dp_x = W // 2 - dead_w // 2
            dp_y = H - 190
            screen.blit(dead_panel, (dp_x, dp_y))

            draw_text(screen, f"Score: {state['score']}", font_mid, (255, 230, 80),
                       W // 2, dp_y + 45)
            draw_text(screen, "SPACE / R to retry", font_small, (200, 200, 220),
                       W // 2, dp_y + 95)

        pygame.display.flip()

    pygame.quit()





if __name__ == "__main__":
    asyncio.run(main())
