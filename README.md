# Mundo das Etiquetas — sistema web reconstruído

**Atenção:** Este é um projeto **reconstruído** a partir do README e relatórios acadêmicos anteriores; NÃO corresponde a recuperação byte a byte dos fontes originais. O arquivo ZIP original não estava disponível.

## Requisitos
Python 3.10+ (recomendado Python 3.12), Django 5.2, navegador atual.

## Como executar no Windows / PyCharm
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations orders
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```
Navegador: http://127.0.0.1:8000/ | Administração: http://127.0.0.1:8000/admin/

## Recursos
- Catálogo de produtos, parametrização de preços no admin, precificação por dimensão/quantidade/material/acabamento.
- Geração de orçamento e conversão em pedido mediante confirmação de e-mail (protótipo, não autenticação robusta).
- API JSON de produtos, cálculo de preço e consulta de status.
- Consulta ViaCEP no navegador, painel staff `/painel/`, testes, acessibilidade básica.
- SQLite local e PostgreSQL por `DATABASE_URL`; Render/Gunicorn/WhiteNoise; GitHub Actions.

## API
- `GET /api/v1/produtos/`
- `POST /api/v1/calcular-preco/` (JSON com `product_id`, `width_cm`, `height_cm`, `quantity`, `material`, `finish`)
- `GET /api/v1/pedidos/<uuid>/status/?email=...`

## Avisos
- As tabelas/regras geradas por `seed_demo` são **preços FICTÍCIOS**, não utilizar em orçamentos reais.
- Em produção configurar `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e `DATABASE_URL`.
- Para implantação comercial implementar autenticação de clientes, proteção contra abuso/rate limiting, controles de privacidade LGPD e política de acesso a orçamentos. Este protótipo NÃO é adequado ao uso comercial sem revisão de segurança.
- O projeto não inclui uma migração gerada; execute `makemigrations orders` antes de `migrate` e versione as migrações geradas.
