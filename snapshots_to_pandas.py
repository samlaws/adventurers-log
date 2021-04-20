import pandas as pd
from api_testing import ApiMethods


def snapshot_to_skills(snapshots):
    sd = []
    for snapshot in snapshots:
        data = {}
        data["date"] = snapshot["createdAt"]
        for k in snapshot.keys():
            try:
                xp = snapshot[k]["experience"]
                data[k] = xp
            except Exception:
                pass

        sd.append(data)

    d = {}
    for k in sd[0].keys():
        d[k] = list(d[k] for d in sd)

    df = pd.DataFrame.from_dict(d)
    df.set_index("date", inplace=True)

    return df
