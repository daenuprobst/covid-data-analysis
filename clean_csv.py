import pandas as pd
import numpy as np


def main():
    df = pd.read_csv("bag_data_11_04.csv")
    df = df[(df["sex"] < 5) & (df["fallklasse"] == "sicherer Fall")]
    df["sex"] = df["sex"].replace(1, "Male").replace(2, "Female")
    df["fall_dt"] = pd.to_datetime(df["fall_dt"], format="%d.%m.%Y")
    df.rename(columns={"altersjahr": "age"}, inplace=True)
    df = df[df["age"] >= 0]
    df["age"] = df["age"].astype(int)
    df["outcome"] = (
        df["Anzahl Todesfälle"].replace(1, "Death").replace(0, "None or Cured")
    )

    df_cantons = pd.read_csv("data_cantons.csv")

    df_age = (
        pd.read_csv("age_dist_2018.csv")
        .sort_values(["canton", "sex", "age"], ascending=True)
        .reset_index()
    )
    df_age_by_canton = df_age.groupby(["canton", "sex"]).sum().reset_index()
    df_age["percentage"] = (
        df_age["count"]
        / df_age_by_canton.loc[df_age_by_canton.index.repeat(99)]["count"].tolist()
    )

    # Set min age to 1 and max age to 99
    df_tmp = df.copy()
    df_tmp["age"] = np.where((df_tmp["age"] > 99), 99, df_tmp["age"])
    df_tmp["age"] = np.where((df_tmp["age"] < 1), 1, df_tmp["age"])
    df_grouped = df.groupby(["Canton", "age", "sex"])

    df_age["cases"] = 0
    df_age["fatalities"] = 0

    # A slightly hacky solution to get the case counts associated with the age distribution
    # Also, a demonstration of how slow python is ;-)
    for canton in df_age["canton"].unique():
        for age in df_age["age"].unique():
            for sex in df_age["sex"].unique():
                if (canton, age, sex) in df_grouped.indices:
                    cases = df_grouped.get_group((canton, age, sex)).sum()[
                        "Anzahl laborbestätigte Fälle"
                    ]
                    fatalities = df_grouped.get_group((canton, age, sex)).sum()[
                        "Anzahl Todesfälle"
                    ]
                    df_age.loc[
                        (df_age["canton"] == canton)
                        & (df_age["age"] == age)
                        & (df_age["sex"] == sex),
                        "cases",
                    ] = cases
                    df_age.loc[
                        (df_age["canton"] == canton)
                        & (df_age["age"] == age)
                        & (df_age["sex"] == sex),
                        "fatalities",
                    ] = fatalities

    df_age["cases_pp"] = df_age["cases"] / df_age["count"]
    df_age["fatalities_pp"] = df_age["fatalities"] / df_age["count"]

    df_age.to_csv("age_distribution_latest.csv", index=False)


if __name__ == "__main__":
    main()
