from requests_html import HTMLSession

def getVehicleImage():
  session = HTMLSession()
  url = f"https://gta.fandom.com/wiki/{'Gauntlet Classic Custom'.replace(' ', '_')}"
  r = session.get(url)
  image_url = r.html.html.split("pi-image-thumbnail")[0].split("image image-thumbnail")[-1].split("src=\"")[1].split("\"")[0]
  return {"wiki_url" : url, "image_url" : image_url}
# end getVehicleImage

print(getVehicleImage())