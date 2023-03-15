from ESPN import ESPN
import pandas

if __name__ == "__main__":
    submissions = pandas.read_csv("./data/2023/submissions.csv")

    for email in submissions["email"]:
        email2 = f"alecjmasterson+{email}@gmail.com"
        with ESPN(email2) as espn:
            espn.login()
            espn.get_brackets()
            1/0
            for index, row in submissions[submissions["email"] == email]:
                if pandas.isna(row["bracket"]) or row["submitted"]:
                    continue
                espn.submit(row["bracket"])
                row["submitted"] = True
