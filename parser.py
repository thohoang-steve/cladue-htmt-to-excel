from bs4 import BeautifulSoup

def extract_data(html):
    soup = BeautifulSoup(html, "html.parser")

    def get_values(selector):
        return [
            el.get("value") or el.text
            for el in soup.select(selector)
            if (el.get("value") or el.text).strip()
        ]

    data = {
        "Name": soup.select_one("#p-name").get("value") if soup.select_one("#p-name") else "",
        "Role": soup.select_one("#p-role").get("value") if soup.select_one("#p-role") else "",
        "Pains": "; ".join(get_values("#pains .li-in")),
        "Goals": "; ".join(get_values("#goals .li-in")),
        "Insights": "; ".join(get_values("#insights .li-in")),
        "Solutions": "; ".join(get_values("#solutions .li-in")),
        "Messages": "; ".join(get_values("#messages .li-in")),
    }

    return data
