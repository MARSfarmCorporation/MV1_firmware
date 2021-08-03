trial = {
    "_id": {
        "$oid": "60db520a1a0f29f5a74a0f62"
    },
    "device_id": "60f1a223786cb0a4a6a5a175",
    "start_date": 1628007453,
    "start_date_str": "2021-07-01 00:41",
    "model_name": "Trial",
    "recipe": [
        {"recipe_id": "60f1cfcd1c80bff2be8d4a94",
         "recipe_name": "marsfarm_photoperiod_14/10",
         "recipe_variable": "photoperiod"
         }
    ],
    "phases": [
        {"name": "growth",
         "phase_start": 0,
         "step": [
            {"temperature": [
                 {
                     "start_time": [0, 0],
                     "setting": 75
                 },
                 {
                     "start_time": [15, 40],
                     "setting": 85
                 }
             ]
             },
            {"light_intensity": [
                 {
                     "start_time": [0, 0],
                     "setting": [0, 0, 0, 0, 0]
                 },
                 {
                     "start_time": [17, 0],
                     "setting": [75, 75, 75, 75, 75]
                 }
             ]
             }
         ]

         },
        {"name": "veg",
         "phase_start": 28,
         "step": [
            {"temperature": [
                 {
                     "start_time": [0, 0],
                     "setting": [75]
                 },
                 {
                     "start_time": [16, 0],
                     "setting": [85]
                 }
             ]
             },
            {"light_intensity": [
                 {
                     "start_time": [0, 0],
                     "setting": [0, 0, 0, 0, 0]
                 },
                 {
                     "start_time": [10, 0],
                     "setting": [75, 75, 75, 75, 75]
                 }
             ]
             }
         ]

         }
    ]
}
