def normalize_params(order_by="estrelas DESC", cidade=None, estrelas_min=0, estrelas_max=5, diaria_min=0, diaria_max=100000000, limit=50, offset=0, **dados):
    
    parametros = {
        "estrelas_min": estrelas_min,
        "estrelas_max": estrelas_max,
        "diaria_min": diaria_min,
        "diaria_max": diaria_max,
        "limit": limit,
        "offset": offset
    }
    if cidade:
        parametros['cidade'] = cidade
    if order_by:
        parametros['order_by'] = order_by
    return parametros

def consulta_sem_cidade(params: dict):
    return f"SELECT * FROM hoteis WHERE (estrelas >= {params['estrelas_min']} AND estrelas <= {params['estrelas_max']}) AND (diaria >= {params['diaria_min']} AND diaria <= {params['diaria_max']}) ORDER BY {params['order_by']} LIMIT {params['limit']} OFFSET {params['offset']}"

def consulta_com_cidade(params: dict):
    return f"SELECT * FROM hoteis WHERE cidade LIKE '%{params['cidade']}%' AND (estrelas >= {params['estrelas_min']} AND estrelas <= {params['estrelas_max']}) AND (diaria >= {params['diaria_min']} AND diaria <= {params['diaria_max']}) LIMIT {params['limit']} OFFSET {params['offset']}"