import pygame
import math
import sort
import datetime
import settings
from settings import getFont
from draw_t import drawTimer

star  = pygame.image.load('./resources/star.png')
shine = pygame.image.load('./resources/shine.png')
luma  = pygame.image.load('./resources/luma.png')
yoshi = pygame.image.load('./resources/yoshi.png')
moon = pygame.image.load('./resources/moon.png')
background = pygame.image.load('./resources/background.png')
sm64BG = pygame.image.load('./resources/sm64.png')
smgBG = pygame.image.load('./resources/smg.png')
smsBG = pygame.image.load('./resources/sms.png')
smg2BG = pygame.image.load('./resources/smg2.png')
smoBG = pygame.image.load('./resources/smo.png')
finishBG = pygame.image.load('./resources/finish_1120.png')

star_counts = (124,44,70)

#387 x 175 scorecards
# slots = [
#     (10,160),(407,160),(804,160),(1201,160),
#     (10,345),(407,345),(804,345),(1201,345),
#     (10,530),(407,530),(804,530),(1201,530),
#     (10,715),(407,715),(804,715),(1201,715), (1600,900)
# ]
#314 x 174 scorecards
# slots = [
#     (5,5),  (324,5),  (643,5),  (962,5),  (1281,5),
#     (5,184),(324,184),(643,184),(962,184),(1281,184),
#     (5,363),(324,363),(643,363),(962,363),(1281,363),
#     (5,542),(324,542),(643,542),(962,542),(1281,542),
#     (5,721),(324,721),(643,721),(962,721),(1281,721),
#     (1600,900)
# ]
#winter 2020 scorecards
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

def collected(tempStars):
    game=""
    buffer=""
    noun="Star"
    if tempStars <= 124:
        game="Super Mario Odyssey"
        noun="Moon"
    elif tempStars <= 168:
        game="Super Mario Sunshine"
        tempStars -= 124
        noun="Shine"
    elif tempStars <= 238:
        game="Super Mario 64"
        tempStars -= 168
        noun="Star"
    if tempStars != 1:
        buffer = "s"
    return " now has " + str(tempStars) + " "+ noun+buffer + " in " + game + "."

def draw(screen, playerLookup, sortedRacers, page):
    screen.blit(pygame.transform.scale(background, (1600,900)), (0,0))
    drawTimer(screen)
    
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
            smocount = smscount = sm64count = 0
            if score < 124:
                bg = smoBG
                smocount = score
            elif score < 168:
                bg = smsBG
                smocount = 124
                smscount = score-124
            elif score < 238:
                bg = sm64BG
                smocount = 124
                smscount = 44
                sm64count = score-168
            img = pygame.transform.scale(bg,(310,138))
            screen.blit(img, (corner[0]+2, corner[1]+2))

            smallBar = 110 #136
            largeBar = 260 #322
            barHeight = 20
            smolength = math.floor((smocount/124)*smallBar)
            #smglength = math.floor((smgcount/120)*largeBar)
            smslength = math.floor((smscount/44)*smallBar)
            sm64length = math.floor((sm64count/70)*smallBar)

            # base boxes
            s = pygame.Surface((smallBar+4, barHeight), pygame.SRCALPHA)
            s.fill((60,60,60,192))
            screen.blit(s, (40+corner[0], 80+corner[1]) )
            screen.blit(s, (190+corner[0], 80+corner[1]) )
            screen.blit(s, (40+corner[0], 110+corner[1]) )
            #screen.blit(s, (190+corner[0], 110+corner[1]) )

            # filled boxes
            r1 = pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 80+corner[1]+2, smolength, barHeight-4])
            r2 = pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 110+corner[1]+2, smslength, barHeight-4])
            r3 = pygame.draw.rect(screen, (150,150,150,254), [190+corner[0]+2, 80+corner[1]+2, sm64length, barHeight-4])
            #r4 = pygame.draw.rect(screen, (150,150,150,254), [190+corner[0]+2, 110+corner[1]+2, smg2length, barHeight-4])

            # individual game counts
            for i, gme in enumerate([(smocount,r1),(smscount,r2),(sm64count,r3)]):
                if gme[0] < star_counts[i]/2:
                    label = getFont(18).render(str(gme[0]), 1, (220,220,220))
                    label_r = label.get_rect(midleft=(gme[1].midright[0]+2, gme[1].midright[1]))
                else:
                    label = getFont(18).render(str(gme[0]), 1, (60,60,60))
                    label_r = label.get_rect(midright=(gme[1].midright[0]-2, gme[1].midright[1]))
                screen.blit(label, label_r)

            # game icons
            screen.blit(moon, (6+corner[0], 75+corner[1]) )
            screen.blit(shine, (6+corner[0], 103+corner[1]) )
            screen.blit(star, (157+corner[0], 70+corner[1]) )
            #screen.blit(yoshi, (157+corner[0], 108+corner[1]) )

        elif currentPlayer.status == "done":    #shows done tag

            test = pygame.transform.scale(finishBG,(310,138))
            screen.blit(test, (corner[0]+2, corner[1]+2))

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