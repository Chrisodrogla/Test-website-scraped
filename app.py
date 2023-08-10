from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import psycopg2
import os
import stdiomask

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# PostgreSQL connection details read from environment variables
db_host = os.getenv("db_host", "dpg-cj9rk99duelc739jgk3g-a.oregon-postgres.render.com")
db_port = os.getenv("db_port", "5432")
db_name = os.getenv("db_name", "postgres123_rx85")
db_user = os.getenv("db_user", "postgres123")
db_password = os.getenv("db_password" ,"yAttIg0ShfQM1xXrfZMQ6UiwHPc64OWG")

# Function to execute SQL queries with parameterization
def execute_sql_query(query, parameters=None):
    try:
        with psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
        ) as connection:
            with connection.cursor() as cursor:
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                if query.strip().lower().startswith("select"):
                    result = cursor.fetchall()
                else:
                    connection.commit()
                    result = None
            return result
    except psycopg2.Error as e:
        print("Error occurred:", str(e))
        return None

# Homepage with charts
@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    # Chart1 - Company Breached Count
    query1 = "SELECT ransomware_name, COUNT(*) FROM public.scraped_data_test_web GROUP BY ransomware_name;"
    chart1_data = execute_sql_query(query1)

    # Chart2 - Overall Company Breached
    query2 = "SELECT COUNT(company) FROM public.scraped_data_test_web;"
    total_company_breached = execute_sql_query(query2)[0][0]

    # Chart3 - Ransomware Count
    query3 = "SELECT COUNT(DISTINCT ransomware_name) FROM public.scraped_data_test_web;"
    total_ransomware = execute_sql_query(query3)[0][0]

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "chart1_data": chart1_data, "total_company_breached": total_company_breached, "total_ransomware": total_ransomware},
    )

# Search Company Page
@app.get("/search", response_class=HTMLResponse)
def search_company_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

# Search Company Results
@app.post("/search/results", response_class=HTMLResponse)
def search_company_results(request: Request, company: str = Form(...)):
    sanitized_company = "%" + company.replace("%", "") + "%"
    query = "SELECT company_description, data_description, data_date, company_website FROM public.scraped_data_test_web WHERE company ILIKE %s;"
    search_results = execute_sql_query(query, (sanitized_company,))

    if search_results:
        return templates.TemplateResponse(
            "search_results.html",
            {"request": request, "search_results": search_results},
        )
    else:
        return templates.TemplateResponse(
            "no_match_found.html",
            {"request": request},
        )
