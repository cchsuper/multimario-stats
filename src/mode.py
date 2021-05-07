import os
import math
import copy
import pygame
import settings
# import mode_602
# import mode_1120
# import mode_246
# import mode_sandbox
import timer
from settings import getFont

games = copy.deepcopy(settings.modeInfo['games'])
for g in games:
    bg = pygame.image.load(os.path.join(settings.baseDir,g['background']))
    icon = pygame.image.load(os.path.join(settings.baseDir,g['icon']))
    g['background'] = bg
    g['icon'] = icon

finishBG = pygame.image.load(os.path.join(settings.baseDir,settings.modeInfo['finish-bg']))
background = pygame.image.load(os.path.join(settings.baseDir,'resources/background.png'))

def draw_old(screen, playerLookup, sortedRacers, page):
    if settings.mode == "602":
        return mode_602.draw(screen, playerLookup, sortedRacers, page)
    elif settings.mode == "1120":
        return mode_1120.draw(screen,playerLookup)
    elif settings.mode == "246":
        return mode_246.draw(screen, playerLookup, sortedRacers, 1)
    elif settings.mode == "sandbox":
        return mode_sandbox.draw(screen, playerLookup, sortedRacers, 1)

def hasCollected(score):
    game=""
    noun=""
    suffix=""
    for g in games:
        if score <= g['count']:
            game = g['name']
            noun = g['collectable']
            break
        score -= g['count']
    
    if score != 1:
        suffix = "s"
    return " now has " + str(score) + " "+ noun+suffix + " in " + game + "."

slots = [
    (7,5),  (325,5),  (643,5),  (961,5),  (1279,5),
    (7,169),(325,169),(643,169),(961,169),(1279,169),
    (7,315),(325,315),(643,315),(961,315),(1279,315),
    (7,461),(325,461),(643,461),(961,461),(1279,461),
    (7,607),(325,607),(643,607),(961,607),(1279,607),
    (7,753),(325,753),(643,753),(961,753),(1279,753),
    (1600,900)
]
length = 314
height = 142

def draw(screen, playerLookup, sortedRacers, page):
    screen.blit(pygame.transform.scale(background, (1600,900)), (0,0))
    timer.drawTimer(screen)
    
    if page == 2:
        slot = 0
        for i, r in enumerate(sortedRacers):
            if 2 < i < 28:
                playerLookup[r].corner = slots[len(slots)-1]
                continue
            if slot >= len(slots):
                playerLookup[r].corner = slots[len(slots)-1]
            else:
                playerLookup[r].corner = slots[slot]
            if slot == 2:
                slot += 3
            else:
                slot += 1
    else:
        slot = 0
        for r in sortedRacers:
            if slot >= len(slots):
                playerLookup[r].corner = slots[len(slots)-1]
            else:
                playerLookup[r].corner = slots[slot]
            if slot == 2:
                slot += 3
            else:
                slot += 1

    #-----------scorecard drawing------------
    for key in playerLookup:
        currentPlayer = playerLookup[key]
        corner = currentPlayer.corner
        
        pygame.draw.rect(screen, (25, 25, 25), [corner[0], corner[1], 314, 142])

        score = currentPlayer.collects
        if currentPlayer.status == "live":
            bg = None
            gameCounts, barLengths, gameMaxes = [], [], []
            done = False
            smallBar, largeBar, barHeight = 110, 260, 20
            for g in games:
                gameCounts.append(0)
                if done:
                    pass
                elif score <= g['count']:
                    bg = g['background']
                    gameCounts[-1] = score
                    done = True
                    score -= g['count']
                else:
                    gameCounts[-1] = g['count']
                    score -= g['count']
                gameMaxes.append(g['count'])
                barLengths.append(math.floor((gameCounts[-1]/g['count'])*smallBar))

            img = pygame.transform.scale(bg,(310,138))
            screen.blit(img, (corner[0]+2, corner[1]+2))

            # base boxes
            s = pygame.Surface((smallBar+4, barHeight), pygame.SRCALPHA)
            s.fill((60,60,60,192))
            screen.blit(s, (40+corner[0], 80+corner[1]) )
            screen.blit(s, (190+corner[0], 80+corner[1]) )
            screen.blit(s, (40+corner[0], 110+corner[1]) )
            if len(games) == 4:
                screen.blit(s, (190+corner[0], 110+corner[1]) )

            # filled boxes
            gray = (150,150,150)
            rects = []
            rects.append(pygame.draw.rect(screen, gray, [40+corner[0]+2, 80+corner[1]+2, barLengths[0], barHeight-4]))
            rects.append(pygame.draw.rect(screen, gray, [40+corner[0]+2, 110+corner[1]+2, barLengths[1], barHeight-4]))
            rects.append(pygame.draw.rect(screen, gray, [190+corner[0]+2, 80+corner[1]+2, barLengths[2], barHeight-4]))
            if len(games) == 4:
                rects.append(pygame.draw.rect(screen, gray, [190+corner[0]+2, 110+corner[1]+2, barLengths[3], barHeight-4]))

            # individual game counts
            for i in range(len(gameCounts)):
                if gameCounts[i] < gameMaxes[i]/2:
                    label = getFont(18).render(str(gameCounts[i]), 1, (220,220,220))
                    label_r = label.get_rect(midleft=(rects[i].midright[0]+2, rects[i].midright[1]))
                else:
                    label = getFont(18).render(str(gameCounts[i]), 1, (60,60,60))
                    label_r = label.get_rect(midright=(rects[i].midright[0]-2, rects[i].midright[1]))
                screen.blit(label, label_r)

            # game icons
            for i, g in enumerate(games):
                if i == 0:
                    x, y = 6, 75
                elif i == 1:
                    x, y = 6, 103
                elif i == 2:
                    x, y = 157, 70
                elif i == 3:
                    x, y = 157, 108
                screen.blit(g['icon'], (x+corner[0], y+corner[1]))

        elif currentPlayer.status == "done":    #shows done tag

            bg = pygame.transform.scale(finishBG,(310,138))
            screen.blit(bg, (corner[0]+2, corner[1]+2))

            # screen.blit(finishBG, (playerLookup[key].corner[0], playerLookup[key].corner[1]))
            doneTag = getFont(60).render("Done!", 1, (220,220,220))
            done_r = doneTag.get_rect(center=((currentPlayer.corner[0]+(length/2), 85+currentPlayer.corner[1])))
            screen.blit(doneTag, done_r)

            label = getFont(24).render(str("Final Time: {0}".format(currentPlayer.completionTime)), 1, (220,220,220))
            label_r = label.get_rect(center=((currentPlayer.corner[0]+(length/2), 125+currentPlayer.corner[1])))
            screen.blit(label, label_r)
        
        else:
            text = ""
            offset = 0
            label = getFont(23).render("Completion: "+str(score)+"/"+str(settings.max_score) +" in "+currentPlayer.completionTime, 1, (220,220,220))
            if currentPlayer.status == "quit":
                text = "Quit"
            elif currentPlayer.status == "disqualified":
                text = "Disqualified"
            elif currentPlayer.status == "noshow":
                label = getFont(20).render("", 1, (220,220,220))
                text = "No-Show"
                offset = 10
            
            textTag = getFont(48).render(text, 1, (255, 0, 0))
            text_r = textTag.get_rect(center=(currentPlayer.corner[0]+(length/2), currentPlayer.corner[1]+80+offset))
            screen.blit(textTag, text_r)
            label_r = label.get_rect(center=(currentPlayer.corner[0]+(length/2), currentPlayer.corner[1]+123))
            screen.blit(label, label_r)

        
        #-------scorecard header-------
        #profile picture
        prof = pygame.transform.scale(currentPlayer.profile, (50,50))
        screen.blit(prof, (8+currentPlayer.corner[0], 8+currentPlayer.corner[1])) 

        #name & place
        color = (220,220,220)
        if currentPlayer.place <=3:
            color = (239,195,0)
        nameRender = getFont(24).render(str(currentPlayer.nameCaseSensitive), 1, color)
        placeRender = getFont(40).render(str(currentPlayer.place), 1, color)

        screen.blit(nameRender, (65+currentPlayer.corner[0], 15+currentPlayer.corner[1]))
        #topright justify the place text
        place_r = placeRender.get_rect(topright=(currentPlayer.corner[0]+304,currentPlayer.corner[1]+5))
        screen.blit(placeRender, place_r)


    pygame.display.flip()
    return screen
