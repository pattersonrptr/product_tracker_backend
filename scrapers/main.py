import time
from celery import group
from tasks import run_scraper

if __name__ == "__main__":
    search_terms = ["python book", "javascript book", "data science book", "machine learning book", "linux book"]

    tasks_group = group(run_scraper.s(term) for term in search_terms)
    group_result = tasks_group.apply_async()

    total = len(group_result.results)

    while not group_result.ready():
        completed = sum(1 for res in group_result.results if res.state == "SUCCESS")
        print(f"Tarefas concluídas: {completed}/{total}")
        time.sleep(5)

    results = group_result.get()
    print("Resultados finais:", results)
