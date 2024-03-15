# other dependencies
import scrubadub
from . import faker_util
from . import vocab
import pandas as pd
import os
import datetime
import numpy as np
import warnings
import pickle
import re
from uuid import uuid4


class Metamorph():
    
    # Class attributes
    _key_mappings_df = None
    _scurbadub_util = scrubadub.Scrubber #TODO: Create scrubadub_util.py to separate the package functions
    _faker_util = faker_util
    _vocab_util = vocab
    _allowed_genders = {'f', 'm', 'female', 'male'}
    _offset_int = None
    
    def __init__(self, 
                 mappings: dict = {}, 
                 key_location: str = os.path.expanduser('~'),
                 active: bool = True) -> None:
        
        self._mappings = mappings 
        self._active = active
        Metamorph._key_location = key_location
        print(f"""
        Model Settings
        --------------
        mappings: {mappings}
        key_location: {key_location}
        active: {active}  
        """)
        super().__init__()
        
    def transform(self, series: pd.Series, type: str, **kwargs) -> pd.Series:
        """The transform method calls internal method depending on the passed type.
        Each _method takes care of the data in a unique way. So make sure you call the right type
        for the data you are transforming.
        
        E.g. key for unique identifiers, date for date shifts

        Args:
            series (pd.Series): pass a pandas series e.g. series['claim_number']
            type (str): the type of metamorph transformation desired: 
                key, random date, push date, full name

        Returns:
            pd.Series: returns a pandas series with the de-identified values
        """
        
        type = type.lower()
        if self._active:
            if type=='key':
                return self._transform_key(series)
            elif type=='full name' or type=='fullname':
                return self._transform_full_name(series, kwargs)
            elif type=='random date':
                return self._transform_randomdate(series, **kwargs)
            elif type=='push date':
                return self._transform_pushdate(series, **kwargs)
            elif type=='medical text':
                return self._transform_medical_text(series, **kwargs)
            else:
                raise ValueError(f"type `{type}` was not found")
        else: 
            # returns the same series without transformations
            warnings.warn("active is deactivated. No values have been transformed. Set active=True to apply Metamorph transformations.")
            return series
        
    def save_keys(self, location: str = None):
        if not location:
            msg = "The keys will be saved on the default location. Use `location = 'your/secure/path' or mortph = Metamporth(key_location = 'your/secure/path')` to save on a secure location."
            warnings.warn(msg)

        location = location or self._key_location

        if location.find('~') >= 0:
            location = location.replace('~', os.path.expanduser('~'))

        mapping_key_file_path = os.path.join(location, "key_mappings.json")
        self._key_mappings_df.to_json(mapping_key_file_path, orient="records")
        print(f"Keys have been saved on {mapping_key_file_path}.")  


    def recover_key_mappings(self, location: str = None) -> pd.Series:
        location = location or self._key_location
        mapping_key_file_path = os.path.join(location, "key_mappings.json")

        try:
            self._key_mappings_df = pd.read_json(mapping_key_file_path)
        except:
            msg = f"Could not find mapping keys in {mapping_key_file_path}. Please pass `location = 'your/secure/path' or mortph = Metamporth(key_location = 'your/secure/path')` to locate your key_mappings.json file.`"
            raise ValueError(msg)

        return self._key_mappings_df
            
        
    @classmethod
    def _transform_key(cls, 
        series: pd.Series,
        save_keys: bool = True,
        **kwargs
        ) -> pd.Series:
        """Internal method used to de-identify unique identifiers such as claim numbers, etc.
        It should be used from the .transform method 
        E.g. morph.transform(series['CLAIM_NUMBER'], 'key')

        Args:
            series (pd.Series): pass a pandas series e.g. series['CLAIM_NUMBER']

        Returns:
            pd.Series: returns a pandas series with the de-identified values
        """

        def generate_uuid(x):
            return str(uuid4())
        
        # Generating fake keys
        data = {"key": series, "fake_key": series.apply(generate_uuid) }
        key_mappings_df = pd.DataFrame(data)
        cls._key_mappings_df = key_mappings_df

        location = kwargs.get("location", None)
        if save_keys: cls.save_keys(cls, location)
        
        return key_mappings_df.fake_key
    
    
    def _transform_full_name(self, series: pd.Series, kwargs = 'raise') -> pd.Series:
        """Internal method used to de-identify full names. Genders should be provided.
        It should be used from the .transform method.
        E.g. morph.transform(series['gender'], 'full name')

        Args:
            series (pd.Series): pass a pandas series e.g. series['gender']
            errors (str, optional): By default if there is no gender, a ValueError will be raised. 
                If you whish to ignore and randomize the gender name, use 'ignore' Defaults to 'raise'.

        Raises:
            ValueError: If the wrong parameter is passed, an error will be raised.
            ValueError: If the genders are not passed, by default an error will be raised.

        Returns:
            pd.Series: returns a pandas series with the de-identified values
        """
        # Replaces other gender categories with mapped categories when provided on instantiation
        series = series.astype(str).replace(self._mappings.get(series.name))
        
        genders_not_found = set(series.astype(str).str.lower().unique()).difference(self._allowed_genders)
        errors = kwargs.get('errors', 'raise')
        if genders_not_found:
            if errors == 'raise':
                print(self._mappings.get(series.name))
                display(series.to_frame('mappings').value_counts())
                raise ValueError(f"Must provide a pandas series with gender identifiers {self._allowed_genders} or pass errors='ignore' to assign a random name to other genders.")
            elif errors == 'ignore':
                msg = f"Random gender names have been assigned for genders {genders_not_found}."
                warnings.warn(msg)
            else:
                raise ValueError(f"Parameter `{errors}` was not recognized by the method. Try errors='ignore', or errors='raise'")
    
        return series.str.lower().apply(lambda x: self._faker_util.get_full_name(gender=x))
    
    def _transform_randomdate(self, series: pd.Series, random_date_window: str = 1, **kwargs) -> pd.Series:
        """Internal method used to de-identify dates.
        It should be used from the .transform method.
        E.g. morph.transform(series['date'], 'date')

        Args:
            series (pd.Series): pass a pandas series e.g. series['date']
            months_window (int, optional): This is the weight of how many months you want to shift on the date.
                The window will be within the same scale of the passed integer, negative to positive. Defaults to 1.

        Returns:
            pd.Series: returns a pandas series with the de-identified values
        """
        if not kwargs.get("random_date_window"):
            msg = f"Using the default random_date_window = 1. Pass random_date_window = 2 for 2 months window for example."
            warnings.warn(msg)

        random_date_window = kwargs.get("random_date_window", random_date_window)

        def randomize(x: int, y: int) -> int:
            """Creates a random ouput to shift the date
            It does not allow the same random number.
            """
            output = np.random.randint(x, y+1)
            if output == 0:
                output = randomize(x, y)
            return output
        
        rand_month_window = kwargs.get('random_date_window', random_date_window)
        
        # offsets the months
        try: shifted_date_ds = series.apply(lambda x: x if pd.isnull(x) else x + pd.DateOffset(months=randomize(-rand_month_window, rand_month_window)))
        except: 
            series = pd.to_datetime(series)
            shifted_date_ds = series.apply(lambda x: x if pd.isnull(x) else x + pd.DateOffset(months=randomize(-rand_month_window, rand_month_window)))
        
        # offsets the day withing the shifted month's available days
        # shifted_date_ds = shifted_date_ds.apply(lambda x: x if pd.isnull(x) else x + pd.DateOffset(days=randomize(1, (x + pd.offsets.MonthEnd()).day ) ))
        shifted_date_ds = shifted_date_ds.apply(lambda x: x.strftime(f"%Y-%m-{randomize(1, (x + pd.offsets.MonthEnd(0)).day-1 )}"))
        
        return pd.to_datetime(shifted_date_ds, errors='coerce').dt.date
    
    def _transform_pushdate(
        self, 
        series: pd.Series,
        push_method: str,
        push_type: str,
        push_window: int,
        push_direction: str = 'forwards',
        push_random_window: bool = False,
        push_limit: datetime.date = datetime.datetime.now().date(),
        **kwargs
        ) -> pd.Series:

        # error handling
        assert push_direction in ['forwards', 'backwards', 'f', 'b'], "push_direction must be forwards(f) or backwards(b). forwards(f) is default."
        assert push_method in ['all', 'each'], "push_method must be all or each"
        assert push_type in ['month', 'day'], "Must be month or day"
        assert (push_window > 0 and type(push_window) == int), "push_window must be greater than 0 and must be of type int or `push_window = 'random'`"
        assert type(push_random_window) == bool, "Must be a boolean value True or False"
        
        # setting variables
        offset_int = push_window
        
        # setting the random offset int for the first time of it is not in the object
        series = pd.to_datetime(series)
        if push_random_window:
            offset_int = self._offset_int or np.random.randint(1, push_window+1)
        
            # preserving the random offset to use in future offsets
            self._offset_int = offset_int
        
        print("PUSH STATUS:")
        if push_type == 'day':
            if push_method == 'all':
                print(f"\t-> Pushing all rows by {offset_int} count on {series.name} on a daily basis.")
                offset_int_direction = offset_int if push_direction == 'forwards' else -offset_int
                results = (series + pd.DateOffset(days=offset_int_direction)).dt.date

            elif push_method == 'each':
                print(f"\t-> Pushing each rows by its own random count with a push_window of {push_window} count on {series.name}.")
                if not push_random_window: 
                    msg = "`push_type = each` always randomizes the push on each item. Set `push_random_window = True` to suppress this warning."
                    warnings.warn(msg)
                offset_int = np.random.randint(1, push_window+1)
                offset_int_direction = offset_int if push_direction == 'forwards' else -offset_int
                results = series.apply(lambda x: x + pd.DateOffset(days=offset_int_direction)).dt.date
            
        elif push_type == 'month':
            if push_method == 'all':
                print(f"\t-> Pushing all rows by {offset_int} count on {series.name} on a monthly basis.")
                offset_int_direction = offset_int if push_direction == 'forwards' else -offset_int
                results = (series + pd.DateOffset(months=offset_int_direction)).dt.date
            elif push_method == 'each':
                print(f"\t-> Pushing each rows by its own random count with a push_window of {push_window} count on {series.name}.")
                if not push_random_window: 
                    msg = "`push_type = each` always randomizes the push on each item. Set `push_random_window = True` to suppress this warning."
                    warnings.warn(msg)
                offset_int = np.random.randint(1, push_window+1)
                offset_int_direction = offset_int if push_direction == 'forwards' else -offset_int
                results = series.apply(lambda x: x + pd.DateOffset(months=offset_int_direction)).dt.date

        # Ensuring the push does not go into the future
        results = results.where(results <= push_limit, push_limit)
        return results
    
    def _transform_medical_text(self,
        series = pd.Series,
        **kwargs
        ) -> pd.Series:

        def generate_text(text):
            text_length = len(text)
            faker_text = self._faker_util.fake.sentence(ext_word_list=self._vocab_util.medical_keywords)
            while len(faker_text) < text_length:
                faker_text += ' ' + self._faker_util.fake.sentence(ext_word_list=self._vocab_util.medical_keywords)           
            return faker_text[:text_length]

        return series.apply(lambda x: generate_text(x))
    

    







            
