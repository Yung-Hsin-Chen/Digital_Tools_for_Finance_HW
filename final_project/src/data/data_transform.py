import numpy as np

class CleanData:

    def __init__(self, df_lst, boundary=300):
        self._df_lst = df_lst
        self._covid_df = df_lst[2]
        self._boundary = boundary
        self._select_col = []

    def get_count(self, df):

        df = df.groupby(["location"])[["date"]].count().rename(columns={"date": "count"})\
            .reset_index()

        return df

    def remove_less_entry_countries(self):

        for i, df in enumerate(self._df_lst):
            below_boundary_country = self.get_count(df)[self.get_count(df)["count"] < self._boundary]\
                                     ["location"].tolist()
            df = df[~df.location.isin(below_boundary_country)]
            self._df_lst[i] = df

        return

    def get_location_without_null(self):

        location_lst = list(set(self._covid_df["location"]))
        select_loc_lst = []
        d = dict.fromkeys(self._covid_df.columns, 0)

        # SELECT COLUMNS HAVING ONLY ONE VALUE PER LOCATION
        for loc in location_lst:
            tmp = self._covid_df[self._covid_df["location"] == loc]
            for col in self._covid_df.columns:
                if len(set(tmp[col])) == 1:
                    d[col] += 1
        self._select_col = list({k: v for k, v in d.items() if v >= 150}.keys())

        # KEEP LOCATIONS THAT DOESN'T HAVE NULL IN THE SELECTED COLUMNS
        for loc in location_lst:
            tmp = self._covid_df[self._covid_df["location"] == loc]
            cnt = 0
            for col in self._select_col:
                if len(set(tmp[col])) == 1:
                    cnt += 1
            if cnt == len(self._select_col):
                select_loc_lst.append(loc)

        for i, df in enumerate(self._df_lst):
            df = df[df["location"].isin(select_loc_lst)]
            self._df_lst[i] = df

        return 

    def select_column_for_vaccine(self):

        keep_col = [["location", "age_group", "people_fully_vaccinated_per_hundred"],
                    ["location", "vaccine", "total_vaccinations"], 
                    ["location", "total_deaths_per_million"]+self._select_col]

        for i, df in enumerate(self._df_lst):
            df = df[np.intersect1d(df.columns, keep_col[i])]
            self._df_lst[i] = df

        return
    
    def clean_data(self):

        self.remove_less_entry_countries()
        self.get_location_without_null()
        self.select_column_for_vaccine()

        return self._df_lst
        