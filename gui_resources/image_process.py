import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((100,100))
file_name = "skill.bmp"

surf = pygame.image.load(file_name).convert()

sys.stdout = open("log.txt" , "w")


pixel_array = pygame.PixelArray(  surf  )

for i in range(len(pixel_array)):
    for j in range(len(pixel_array[0])):
        color = surf.unmap_rgb( pixel_array[i][j] )
        r , g , b= color[0] , color[1] , color[2]
        print r , g, b
        if r > 200 and g > 200 and b > 200:
            pixel_array[i][j] = pygame.Color(247,0,255)


pygame.image.save(pixel_array.make_surface() , "new_" + file_name)

