from faker import Faker
import numpy as np

fake = Faker()

def get_full_name(gender):
    if gender.lower() == "female":
        return fake.name_female()
    elif gender.lower() == "male":
        return fake.name_male()
    else:
        if np.random.randint(0, 100) > 50:
            return fake.name_male() 
        else:
            return fake.name_female()