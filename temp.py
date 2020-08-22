def getTiers(key_info_range, overall_lap_time_range, vehicle):
  return
  key_info = RandomSupport.arrayFromRange(key_info_range)
  key_info = key_info[2:] # row 3:end

  overall_lap_times = RandomSupport.arrayFromRange(overall_lap_time_range)
  overall_lap_times = overall_lap_times[2:] # row 3:end

  # tiers = {S : [[car1, delta], ...], A : []} delta is difference between car and og vehicle
  tiers = {}
  for i in range(len(overall_lap_times)):
    if overall_lap_times[i][2] != vehicle._Class: # class match
      continue

    for j in range(len(key_info)):
      if key_info[j][0] != vehicle._Class: # class match
        continue

      veh_name = key_info[j][1]
      if veh_name == overall_lap_times[i][3]: # vehicle match
        race_tier = key_info[i][4]
        if race_tier not in tiers:
          tiers[race_tier] = []
        tiers[race_tier] = [[veh_name, getDetla(overall_lap_times[i][4], vehicle._Lap_Time__m_ss_000_)]]
  return tiers

def getTiers(car_class):
    url = f"https://broughy.com/gta5{car_classes[car_class]}"
    soup = bsoup(requests.get(url).text, "html.parser")
    tier_lists = str(soup).split("<strong>")[1:]
    tier_lists = [t.split("</div>")[0] for t in tier_lists]
    tiers = {}
    for t in tier_lists:
      tier = t.split("</")[0]
      cars = t.split("<br/>")
      cars[-1] = cars[-1].split("</p>")[0]
      cars[0] = cars[0].split(">")[-1]
      tiers[tier] = cars

    # tiers = {S : [car1, car2...], A : []}
    return tiers
  # end getTier

getTiers("a", "b", "c")