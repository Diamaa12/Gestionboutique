import os
from PIL import Image
chemin = os.path.join(os.path.dirname(__file__), "../resources/images")
if not os.path.exists(chemin):
    os.makedirs(chemin)
image = Image.open(chemin + "/my_icone.png")

#Tailles souhaitées
sizes = [(16, 16), (24, 24), (48, 48)]
try:
    for size in sizes:
        resize_image = image.resize(size)
        resize_image.save(chemin + "/icon_" + str(size[0]) + ".ico")
        print("Image enregistrés dans {chemin}".format(chemin=chemin))
except Exception as e:
    print(e)