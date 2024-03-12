# other dependencies
import scrubadub
import names
import pandas as pd
import os
import datetime
import numpy as np
import warnings
import pickle
import re

class Metamorph(scrubadub.Scrubber):
    
    # Class attributes
    _key_names = []
    _metamorph_keys = {'Docstring': 'Index 0: Key, Index 1: Original Value. Use series.replace(*array) to revert.', 
                       'KeyPair': {}}
    _allowed_genders = {'f', 'm', 'female', 'male'}
    _offset_int = None
    
    def __init__(self, 
                 mappings: dict = {}, 
                 push_method: str = 'all',
                 push_type: str = 'month',
                 push_window: int = 1, 
                 push_random_window: bool = False,
                 push_date_limit: datetime.date = None,
                 random_date_window: int = 1,
                 morphed_key_location: str = os.path.expanduser('~'),
                 active: bool = True) -> None:
        
        # error handling
        assert push_method in ['all', 'each'], "Must be all or each"
        assert push_type in ['month', 'day'], "Must be month or day"
        assert push_window > 0 and type(push_window) == int, "Must be greater than 0 and int"
        assert type(push_random_window) == bool, "Must be a boolean value True or False"
        
        self._mappings = mappings 
        self._push_method = push_method 
        self._push_type = push_type
        self._push_window = push_window
        self._random_push_window = push_random_window
        self._random_date_window = random_date_window
        self._push_date_limit = push_date_limit
        self._active = active
        Metamorph._morphed_key_location = morphed_key_location
        print(f"""
        Model Settings
        --------------
        mappings: {mappings}
        push_method (all, each): {push_method}
        push_type (month, day): {push_type}
        push_months_window: {push_window}
        push_random_window (True, False): {push_random_window}
        push_date_limit: {push_date_limit}
        random_date_window: {random_date_window}
        morphed_key_location: {morphed_key_location}
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
            else:
                raise ValueError(f"type `{type}` was not found")
        else: 
            # returns the same series without transformations
            warnings.warn("active is deactivated. No values have been transformed. Set active=True to apply Metamorph transformations.")
            return series
        
    def save_keys(self, location):
        
        if location.find('~') >= 0:
            location = location.replace('~', os.path.expanduser('~'))
        # saving keys in .pickle file
        with open(os.path.join(location, 'metamorph.pickle'), 'wb') as f:
            pickle.dump(self._metamorph_keys, f)
        
    def recoverkey(self, series: pd.Series) -> pd.Series:
        #PSEUDO: 
        with open(os.path.join(self._morphed_key_location, 'metamorph.pickle'), 'rb') as f:
            keys = pickle.load(f)
            
        
    @classmethod
    def _transform_key(cls, series: pd.Series) -> pd.Series:
        """Internal method used to de-identify unique identifiers such as claim numbers, etc.
        It should be used from the .transform method 
        E.g. morph.transform(series['CLAIM_NUMBER'], 'key')

        Args:
            series (pd.Series): pass a pandas series e.g. series['CLAIM_NUMBER']

        Returns:
            pd.Series: returns a pandas series with the de-identified values
        """
        def random_id(x: str) -> str:
            """
            Creates a random id from numerical ids passed to the class.
            It does not allow the same random id.
            """
            # creating new random id
            random_range = ('1'+'0'*(len(x)-1), '9'*len(x))
            output = np.random.randint(*random_range)
            
            # handling same value id before return
            if output==int(x): 
                return random_id(x)
            return output
        
        # de-identifying on unique ids
        unique_ids = pd.Series(series.astype(str).unique())
        keys_value_np = np.array(list(map(lambda x: (x, random_id(re.sub('\D', '', x))), unique_ids)))
        
        # keeping track of transformations
        cls._key_names.append(series.name)
        cls._metamorph_keys['KeyPair'].setdefault(series.name, keys_value_np.T[::-1])
        
        return series.astype(str).replace(*keys_value_np.T)
    
    
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
        series = series.astype(str).str.replace('.0','').replace(self._mappings.get(series.name))
        
        genders_not_found = set(series.astype(str).str.lower().unique()).difference(self._allowed_genders)
        errors = kwargs.get('errors', 'raise')
        if genders_not_found:
            if errors == 'raise':
                print(self._mappings.get(series.name))
                display(series.to_frame('mappings').value_counts())
                raise ValueError(f"Must provide a pandas series with gender identifiers {self._allowed_genders} or pass errors='ignore' to assign a random gender name.")
            elif errors == 'ignore':
                warnings.warn(f"Random gender names have been assigned for genders {genders_not_found}.")
            else:
                raise ValueError(f"Parameter `{errors}` was not recognized by the method. Try errors='ignore', or errors='raise'")
    
        return series.str.lower().apply(lambda x: names.get_full_name(gender=x))
    
    def _transform_randomdate(self, series: pd.Series, **kwargs) -> pd.Series:
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
        def randomize(x: int, y: int) -> int:
            """Creates a random ouput to shift the date
            It does not allow the same random number.
            """
            output = np.random.randint(x, y+1)
            if output == 0:
                output = randomize(x, y)
            return output
        
        rand_month_window = kwargs.get('random_date_window', self._random_date_window)
        
        # offsets the months
        shifted_date_ds = series.apply(lambda x: x if pd.isnull(x) else x + pd.DateOffset(months=randomize(-rand_month_window, rand_month_window)))
        
        # offsets the day withing the shifted month's available days
        # shifted_date_ds = shifted_date_ds.apply(lambda x: x if pd.isnull(x) else x + pd.DateOffset(days=randomize(1, (x + pd.offsets.MonthEnd()).day ) ))
        shifted_date_ds = shifted_date_ds.apply(lambda x: x.strftime(f"%Y-%m-{randomize(1, (x + pd.offsets.MonthEnd(0)).day-1 )}"))
        
        return pd.to_datetime(shifted_date_ds, errors='coerce').dt.date
    
    def _transform_pushdate(self, series: pd.Series) -> pd.Series:
        
        # setting variables
        push_method = self._push_method
        push_type = self._push_type
        offset_int = self._push_window
        
        # setting the random offset int for the first time of it is not in the object
        if self._random_push_window:
            offset_int = self._offset_int or np.random.randint(1, self._push_window+1)
        
            # preserving the random offset to use in future offsets
            self._offset_int = offset_int
        
        
        if push_type == 'day':
            if push_method == 'all':
                return (series + pd.DateOffset(days=offset_int)).dt.date
            elif push_method == 'each':
                if not self._random_push_window: warnings.warn("push_type each always randomizes the push. Use push_type = 'all' when push_random_window is False")
                return series.apply(lambda x: x + pd.DateOffset(days=np.random.randint(1, self._push_window+1))).dt.date