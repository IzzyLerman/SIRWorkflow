import datetime
import pandas
import numpy
import math

def getSIRData() -> None:


    def _jhu_us_daily_url(date) -> str:
        # JHU file naming convention: MM-DD-YYYY.csv
        date_str = date.strftime("%m-%d-%Y")
        return (
            "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/refs/heads/"
            f"master/csse_covid_19_data/csse_covid_19_daily_reports_us/{date_str}.csv"
        )

    def get(df: pandas.DataFrame, col: str, required: bool = True, default=None):
        col_l = col.lower()
        if col_l not in df.columns:
            if required:
                raise RuntimeError(f"Required column '{col}' missing in {url}. ")
            return default
        return row[col_l]


    start_date = datetime.date(2020,4,14)
    days = 30
    infectious_period_days = 7
    oregon_2020_pop = 4237256
    ny_2020_pop = 20201249
    out_filename = "SIR_init_conditions.csv"

    state_name = "New York"
    records = []

    for k in range(days):
        d = start_date + datetime.timedelta(days=k)
        url = _jhu_us_daily_url(d)
        try:
            df = pandas.read_csv(url)
        except Exception as e:
            raise RuntimeError(f"failed to fetch {url}: {e}")

        df.columns = [c.lower() for c in df.columns]

        if "province_state" not in df.columns:
            raise RuntimeError(f"'province_state' column not found in {url}. ")

        row = df[df["province_state"] == state_name]
        if row.empty:
            raise RuntimeError(f"No row for {state_name} on {d} in {url}")

        row = row.iloc[0]

        confirmed = float(get(df,"confirmed"))
        deaths = float(get(df,"deaths"))
        recovered = float(get(df,"recovered", required=False, default=0.0))
        active = float(get(df,"active", required=False, default=confirmed - deaths - recovered))

        N = oregon_2020_pop

        R_t = recovered + deaths
        I_t = active
        S_t = N - I_t - R_t

        records.append(
            {
                "date": d,
                "N": N,
                "S": S_t,
                "I": I_t,
                "R": R_t,
            }
        )

    data = pandas.DataFrame(records)
    day0 = data.iloc[0]




    # Estimate growth rate r from log(I_t) on days where I_t > 0
    mask = data["I"] > 0
    if mask.sum() < 2:
        # Not enough data to fit a slope;
        raise RuntimeError(f"Not enough non-zero I values. Try increasing t_max")
    else:
        t_vals = numpy.arange(len(data))[mask].astype(float)
        log_I = numpy.log(data.loc[mask, "I"].values.astype(float))
        # Fit log(I_t) ~ a + r * t  => slope = r
        slope, intercept = numpy.polyfit(t_vals, log_I, 1)
        r_est = float(slope)

    # Recovery rate gamma from assumed infectious period
    gamma = 1.0 / infectious_period_days

    beta = r_est + gamma
    beta = max(beta, 0.0)

    I0 = max(float(day0["I"]), 1.0) # avoid zero for logs
    R0 = max(float(day0["R"]), 0.0)
    N = oregon_2020_pop

    out_data = pandas.DataFrame({
        "beta": [beta],
        "gamma": [gamma],
        "N": [N],
        "I0": [I0], 
        "R0": [R0],
        "S0": [max(N - I0 - R0, 0.0)],
        "tmax": [days]
    })

    out_data.to_csv(out_filename, index=False)
    faasr_put_file(out_filename, out_filename)


if __name__ == '__main__':
    getSIRData()
