from src.app.infrastructure.repositories.search_config_repository import (
    SearchConfigRepository,
)
from src.app.entities import search_config as SearchConfigEntity
from datetime import datetime, timezone, time
from types import SimpleNamespace
from unittest.mock import MagicMock


def test_create_search_config():
    # Mock da sessão do banco de dados
    db_mock = MagicMock()

    # Instância do repositório
    repository = SearchConfigRepository(db_mock)

    # Dados de entrada para a entidade SearchConfig
    search_config_entity = SearchConfigEntity.SearchConfig(
        search_term="test create",
        is_active=True,
        frequency_days=7,
        preferred_time=time(10, 0),
        user_id=1,
        search_metadata={"key": "value"},
    )

    # Mock do modelo retornado pelo banco de dados após a criação
    mock_db_model = SimpleNamespace(
        id=1,
        search_term="test create",
        is_active=True,
        frequency_days=7,
        preferred_time=time(10, 0),
        search_metadata={"key": "value"},
        user_id=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        source_websites=[],
    )
    # Mock do modelo retornado pelo banco de dados após a criação
    mock_db_model = SimpleNamespace(
        id=1,
        search_term="test create",
        is_active=True,
        frequency_days=7,
        preferred_time=time(10, 0),
        search_metadata={"key": "value"},
        user_id=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        source_websites=[],
    )

    # Configura o mock_db_model para ser o retorno de refresh
    db_mock.add.return_value = None
    # Adicionamos a linha abaixo para mockar o objeto que será "refreshed"
    db_mock.refresh.side_effect = lambda obj: setattr(
        obj, "__dict__", mock_db_model.__dict__
    )
    db_mock.commit.return_value = None

    # Chama o método create
    result = repository.create(search_config_entity)

    # Asserts
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once()

    assert result.id == 1
    assert result.search_term == "test create"
    assert result.is_active is True
    assert result.frequency_days == 7
    assert result.preferred_time == time(10, 0)
    assert result.user_id == 1
    assert result.search_metadata == {"key": "value"}


def test_get_by_id_search_config():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    # Mock do objeto SearchConfigModel que seria retornado pelo banco
    mock_db_model = SimpleNamespace(
        id=1,
        search_term="test get by id",
        is_active=True,
        frequency_days=1,
        preferred_time=time(12, 0),
        search_metadata={"source": "mock"},
        user_id=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        source_websites=[
            SimpleNamespace(
                id=101,
                name="Website A",
                base_url="http://websitea.com",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                products=[],  # Para evitar recursão em entidades aninhadas nos mocks
            )
        ],
    )
    # Configura o mock para o .first() do query
    db_mock.query.return_value.options.return_value.options.return_value.options.return_value.filter.return_value.first.return_value = mock_db_model

    # Chama o método get_by_id
    result = repository.get_by_id(1)

    # Asserts
    assert result is not None
    assert result.id == 1
    assert result.search_term == "test get by id"
    assert len(result.source_websites) == 1
    assert result.source_websites[0].name == "Website A"

    # Testa o caso de não encontrar
    db_mock.query.return_value.options.return_value.options.return_value.options.return_value.filter.return_value.first.return_value = None
    result = repository.get_by_id(999)
    assert result is None


def test_get_all_search_configs_no_filters():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            search_term="Test 1",
            is_active=True,
            frequency_days=1,
            preferred_time=time(10, 0),
            search_metadata={"key": "value1"},
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Test 2",
            is_active=False,
            frequency_days=7,
            preferred_time=time(14, 0),
            search_metadata={"key": "value2"},
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            source_websites=[],
        ),
    ]

    # Cria um mock para o objeto de query do SQLAlchemy
    mock_query_obj = MagicMock()

    # Faz com que as chamadas .options() retornem o próprio mock_query_obj para encadeamento
    mock_query_obj.options.return_value = mock_query_obj

    # Faz com que .filter(), .order_by(), .offset(), .limit() retornem o próprio mock_query_obj
    # para que as chamadas a .all() e .count() possam ser feitas nele.
    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    # Configura os valores de retorno finais para .all() e .count()
    mock_query_obj.all.return_value = mock_db_models
    mock_query_obj.count.return_value = len(mock_db_models)

    # Configura o db_mock.query para retornar nosso mock_query_obj
    db_mock.query.return_value = mock_query_obj

    # Chama o método get_all sem nenhum filtro ou ordenação, mas com os limites padrão
    search_configs, total_count = repository.get_all()

    # Asserts
    assert len(search_configs) == 2
    assert total_count == 2
    assert search_configs[0].search_term == "Test 1"
    assert search_configs[1].search_term == "Test 2"

    # Verificações de chamadas
    db_mock.query.assert_called_once()
    # Verifica que options foi chamado 3 vezes (como na implementação real)
    assert mock_query_obj.options.call_count == 3

    # Verifica que count foi chamado
    mock_query_obj.count.assert_called_once()

    # Verifica que limit foi chamado com o valor padrão
    mock_query_obj.limit.assert_called_once_with(10)  # O valor padrão é 10

    # Verifica que offset foi chamado com o valor padrão
    mock_query_obj.offset.assert_called_once_with(0)  # O valor padrão é 0

    # Verifica que all foi chamado
    mock_query_obj.all.assert_called_once()

    # Como não passamos filtros nem sort_by, esses não devem ser chamados
    mock_query_obj.filter.assert_not_called()
    mock_query_obj.order_by.assert_not_called()


def test_get_all_search_configs_with_filters():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            search_term="Laptop",
            is_active=True,
            frequency_days=1,
            preferred_time=time(9, 0),
            search_metadata={"category": "electronics"},
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Smartphone",
            is_active=False,
            frequency_days=3,
            preferred_time=time(14, 30),
            search_metadata={"category": "electronics"},
            user_id=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=3,
            search_term="Monitor",
            is_active=True,
            frequency_days=7,
            preferred_time=time(8, 0),
            search_metadata={"category": "peripherals"},
            user_id=2,
            created_at=datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
    ]

    # Mock para o objeto de query do SQLAlchemy
    mock_query_obj = MagicMock()

    # Faz com que as chamadas .options() retornem o próprio mock_query_obj para encadeamento
    mock_query_obj.options.return_value = mock_query_obj

    # Faz com que .filter(), .order_by(), .offset(), .limit() retornem o próprio mock_query_obj
    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    # Configura os valores de retorno finais para .all() e .count() para o caso filtrado
    filtered_models = [mock_db_models[0]]  # Apenas 'Laptop'
    mock_query_obj.all.return_value = filtered_models
    mock_query_obj.count.return_value = len(filtered_models)

    # Configura o db_mock.query para retornar nosso mock_query_obj
    db_mock.query.return_value = mock_query_obj

    # Teste com filtro por 'search_term'
    filter_data = {"search_term": {"value": "Laptop", "operator": "equals"}}
    search_configs, total_count = repository.get_all(
        column_filters=filter_data, limit=10, offset=0
    )

    # Asserts
    assert len(search_configs) == 1
    assert total_count == 1
    assert search_configs[0].search_term == "Laptop"

    # Verificações de chamadas
    db_mock.query.assert_called_once()
    assert mock_query_obj.options.call_count == 3
    assert mock_query_obj.filter.call_count == len(
        filter_data
    )  # Filter deve ter sido chamado para cada filtro
    mock_query_obj.count.assert_called_once()
    mock_query_obj.limit.assert_called_once_with(10)
    mock_query_obj.offset.assert_called_once_with(0)
    mock_query_obj.all.assert_called_once()
    mock_query_obj.order_by.assert_not_called()  # Nenhuma ordenação especificada


def test_get_all_search_configs_with_sorting():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            search_term="Banana",
            is_active=True,
            frequency_days=5,
            preferred_time=time(10, 0),
            search_metadata={},
            user_id=1,
            created_at=datetime(2023, 1, 5, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 5, 10, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Apple",
            is_active=False,
            frequency_days=2,
            preferred_time=time(14, 0),
            search_metadata={},
            user_id=1,
            created_at=datetime(2023, 1, 2, 11, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, 11, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=3,
            search_term="Cherry",
            is_active=True,
            frequency_days=1,
            preferred_time=time(8, 0),
            search_metadata={},
            user_id=2,
            created_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
    ]

    # Mock para o objeto de query do SQLAlchemy
    mock_query_obj = MagicMock()

    # Faz com que as chamadas .options() retornem o próprio mock_query_obj para encadeamento
    mock_query_obj.options.return_value = mock_query_obj

    # Faz com que .filter(), .order_by(), .offset(), .limit() retornem o próprio mock_query_obj
    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    # Configura os valores de retorno finais para .all() e .count()
    # Para ordenação, mockamos os dados já ordenados como esperamos
    sorted_models_asc = [
        mock_db_models[1],
        mock_db_models[0],
        mock_db_models[2],
    ]  # Apple, Banana, Cherry
    mock_query_obj.all.return_value = sorted_models_asc
    mock_query_obj.count.return_value = len(mock_db_models)

    # Configura o db_mock.query para retornar nosso mock_query_obj
    db_mock.query.return_value = mock_query_obj

    # Teste com ordenação ascendente por 'search_term'
    search_configs, total_count = repository.get_all(
        sort_by="search_term", sort_order="asc", limit=10, offset=0
    )

    # Asserts para ordenação ascendente
    assert len(search_configs) == 3
    assert total_count == 3
    assert search_configs[0].search_term == "Apple"
    assert search_configs[1].search_term == "Banana"
    assert search_configs[2].search_term == "Cherry"

    # Verificações de chamadas
    db_mock.query.assert_called_once()
    assert mock_query_obj.options.call_count == 3
    mock_query_obj.order_by.assert_called_once()  # order_by deve ter sido chamado
    mock_query_obj.count.assert_called_once()
    mock_query_obj.limit.assert_called_once_with(10)
    mock_query_obj.offset.assert_called_once_with(0)
    mock_query_obj.all.assert_called_once()
    mock_query_obj.filter.assert_not_called()  # Nenhum filtro especificado

    # Resetar mocks para o próximo cenário de teste de ordenação
    db_mock.reset_mock()

    # Configurar novamente o mock_query_obj para a nova chamada de query
    mock_query_obj = MagicMock()
    mock_query_obj.options.return_value = mock_query_obj
    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    sorted_models_desc = [
        mock_db_models[2],
        mock_db_models[0],
        mock_db_models[1],
    ]  # Cherry, Banana, Apple
    mock_query_obj.all.return_value = sorted_models_desc
    mock_query_obj.count.return_value = len(mock_db_models)
    db_mock.query.return_value = mock_query_obj

    # Teste com ordenação descendente por 'search_term'
    search_configs_desc, total_count_desc = repository.get_all(
        sort_by="search_term", sort_order="desc", limit=10, offset=0
    )

    # Asserts para ordenação descendente
    assert len(search_configs_desc) == 3
    assert total_count_desc == 3
    assert search_configs_desc[0].search_term == "Cherry"
    assert search_configs_desc[1].search_term == "Banana"
    assert search_configs_desc[2].search_term == "Apple"

    # Verificações de chamadas para o segundo caso
    db_mock.query.assert_called_once()
    assert mock_query_obj.options.call_count == 3
    mock_query_obj.order_by.assert_called_once()
    mock_query_obj.count.assert_called_once()
    mock_query_obj.limit.assert_called_once_with(10)
    mock_query_obj.offset.assert_called_once_with(0)
    mock_query_obj.all.assert_called_once()
    mock_query_obj.filter.assert_not_called()


def test_get_all_search_configs_with_filters_and_sorting():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    mock_db_models = [
        SimpleNamespace(
            id=1,
            search_term="Monitor 27 inch",
            is_active=True,
            frequency_days=7,
            preferred_time=time(10, 0),
            search_metadata={"type": "electronics"},
            user_id=1,
            created_at=datetime(2023, 1, 10, 10, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 10, 10, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Smart TV 55 inch",
            is_active=True,
            frequency_days=1,
            preferred_time=time(14, 0),
            search_metadata={"type": "electronics"},
            user_id=2,
            created_at=datetime(2023, 1, 12, 14, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 12, 14, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=3,
            search_term="Laptop Gamer",
            is_active=False,
            frequency_days=3,
            preferred_time=time(8, 0),
            search_metadata={"type": "electronics"},
            user_id=1,
            created_at=datetime(2023, 1, 11, 8, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 11, 8, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
        SimpleNamespace(
            id=4,
            search_term="Keyboard Mechanical",
            is_active=True,
            frequency_days=7,
            preferred_time=time(16, 0),
            search_metadata={"type": "peripherals"},
            user_id=2,
            created_at=datetime(2023, 1, 9, 16, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 9, 16, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
    ]

    # Mock para o objeto de query do SQLAlchemy
    mock_query_obj = MagicMock()

    # Faz com que as chamadas .options() retornem o próprio mock_query_obj para encadeamento
    mock_query_obj.options.return_value = mock_query_obj

    # Faz com que .filter(), .order_by(), .offset(), .limit() retornem o próprio mock_query_obj
    mock_query_obj.filter.return_value = mock_query_obj
    mock_query_obj.order_by.return_value = mock_query_obj
    mock_query_obj.offset.return_value = mock_query_obj
    mock_query_obj.limit.return_value = mock_query_obj

    # Cenario: is_active=True e search_term contendo "inch", ordenado por search_term ASC
    # Resultados esperados: Monitor 27 inch, Smart TV 55 inch
    filtered_and_sorted_models = [
        mock_db_models[0],  # Monitor 27 inch
        mock_db_models[1],  # Smart TV 55 inch
    ]

    mock_query_obj.all.return_value = filtered_and_sorted_models
    mock_query_obj.count.return_value = len(filtered_and_sorted_models)

    db_mock.query.return_value = mock_query_obj

    filter_data = {
        "is_active": {"value": True, "operator": "equals"},
        "search_term": {"value": "inch", "operator": "contains"},
    }
    search_configs, total_count = repository.get_all(
        column_filters=filter_data,
        sort_by="search_term",
        sort_order="asc",
        limit=10,
        offset=0,
    )

    assert len(search_configs) == 2
    assert total_count == 2
    assert search_configs[0].search_term == "Monitor 27 inch"
    assert search_configs[1].search_term == "Smart TV 55 inch"

    # Verificações de chamadas
    db_mock.query.assert_called_once()
    assert mock_query_obj.options.call_count == 3
    assert mock_query_obj.filter.call_count == len(filter_data)
    mock_query_obj.order_by.assert_called_once()  # order_by deve ter sido chamado
    mock_query_obj.count.assert_called_once()
    mock_query_obj.limit.assert_called_once_with(10)
    mock_query_obj.offset.assert_called_once_with(0)
    mock_query_obj.all.assert_called_once()

    # Resetar mocks para um novo cenário
    db_mock.reset_mock()

    # Cenario: user_id=2, ordenado por updated_at DESC
    # Resultados esperados: Keyboard Mechanical, Monitor 27 inch (se for mockado com user_id=2 e depois user_id=1 para o monitor)
    # Reajustando mock_db_models para refletir os dados que seriam retornados em um cenário real
    filtered_and_sorted_models_2 = [
        SimpleNamespace(
            id=4,
            search_term="Keyboard Mechanical",
            is_active=True,
            frequency_days=7,
            preferred_time=time(16, 0),
            search_metadata={"type": "peripherals"},
            user_id=2,
            created_at=datetime(2023, 1, 9, 16, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(
                2023, 1, 15, 16, 0, 0, tzinfo=timezone.utc
            ),  # Updated mais recente
            source_websites=[],
        ),
        SimpleNamespace(
            id=2,
            search_term="Smart TV 55 inch",
            is_active=True,  # Ajustando para True para ser incluído
            frequency_days=1,
            preferred_time=time(14, 0),
            search_metadata={"type": "electronics"},
            user_id=2,
            created_at=datetime(2023, 1, 12, 14, 0, 0, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 12, 14, 0, 0, tzinfo=timezone.utc),
            source_websites=[],
        ),
    ]

    mock_query_obj_2 = MagicMock()
    mock_query_obj_2.options.return_value = mock_query_obj_2
    mock_query_obj_2.filter.return_value = mock_query_obj_2
    mock_query_obj_2.order_by.return_value = mock_query_obj_2
    mock_query_obj_2.offset.return_value = mock_query_obj_2
    mock_query_obj_2.limit.return_value = mock_query_obj_2
    mock_query_obj_2.all.return_value = filtered_and_sorted_models_2
    mock_query_obj_2.count.return_value = len(filtered_and_sorted_models_2)
    db_mock.query.return_value = mock_query_obj_2

    filter_data_2 = {
        "user_id": {"value": 2, "operator": "equals"},
    }
    search_configs_2, total_count_2 = repository.get_all(
        column_filters=filter_data_2,
        sort_by="updated_at",
        sort_order="desc",
        limit=10,
        offset=0,
    )

    assert len(search_configs_2) == 2
    assert total_count_2 == 2
    assert search_configs_2[0].search_term == "Keyboard Mechanical"  # Mais recente
    assert search_configs_2[1].search_term == "Smart TV 55 inch"

    # Verificações de chamadas para o segundo cenário
    db_mock.query.assert_called_once()
    assert mock_query_obj_2.options.call_count == 3
    assert mock_query_obj_2.filter.call_count == len(filter_data_2)
    mock_query_obj_2.order_by.assert_called_once()
    mock_query_obj_2.count.assert_called_once()
    mock_query_obj_2.limit.assert_called_once_with(10)
    mock_query_obj_2.offset.assert_called_once_with(0)
    mock_query_obj_2.all.assert_called_once()


def test_update_search_config_basic_fields():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    # 1. Mock do objeto SearchConfigModel existente no banco
    existing_db_model = SimpleNamespace(
        id=1,
        search_term="Old Term",
        is_active=True,
        frequency_days=7,
        preferred_time=time(9, 0),
        search_metadata={"initial": "value"},
        user_id=1,
        created_at=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        source_websites=[],
    )

    # 2. Mock do objeto retornado pelo .first() do query (o item a ser atualizado)
    db_mock.query.return_value.filter.return_value.first.return_value = (
        existing_db_model
    )

    # Mock do get_by_id interno chamado após o refresh (simulando o estado após o update)
    # Criamos um novo mock para o get_by_id para evitar conflitos com o mock original de query
    mock_get_by_id_result = SimpleNamespace(
        id=1,
        search_term="New Term",
        is_active=False,
        frequency_days=3,
        preferred_time=time(15, 30),
        search_metadata={"updated": "value"},
        user_id=1,  # user_id não deve mudar por update
        created_at=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime.now(
            timezone.utc
        ),  # updated_at é atualizado automaticamente
        source_websites=[],
    )
    # Importante: Como `update` chama `get_by_id`, precisamos mockar o `get_by_id` do próprio repositório
    # A maneira mais limpa de fazer isso é mockar o método `get_by_id` na instância do repositório
    repository.get_by_id = MagicMock(
        return_value=SearchConfigEntity.SearchConfig(
            id=mock_get_by_id_result.id,
            search_term=mock_get_by_id_result.search_term,
            is_active=mock_get_by_id_result.is_active,
            frequency_days=mock_get_by_id_result.frequency_days,
            preferred_time=mock_get_by_id_result.preferred_time,
            search_metadata=mock_get_by_id_result.search_metadata,
            user_id=mock_get_by_id_result.user_id,
            created_at=mock_get_by_id_result.created_at,
            updated_at=mock_get_by_id_result.updated_at,
            source_websites=[],
        )
    )

    # 3. Dados de atualização
    update_entity = SearchConfigEntity.SearchConfig(
        search_term="New Term",
        is_active=False,
        frequency_days=3,
        preferred_time=time(15, 30),
        user_id=1,  # O user_id é necessário para a entidade, mas não deve ser atualizado pelo update
        search_metadata={"updated": "value"},
    )

    # 4. Chama o método update
    result = repository.update(1, update_entity)

    # 5. Asserts
    assert result is not None
    assert result.id == 1
    assert result.search_term == "New Term"
    assert result.is_active is False
    assert result.frequency_days == 3
    assert result.preferred_time == time(15, 30)
    assert result.search_metadata == {"updated": "value"}
    assert result.user_id == 1  # user_id não deve ter sido alterado

    # Verificações de chamadas ao mock do DB
    db_mock.query.assert_called_once()  # Chamado para buscar o SearchConfigModel
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(
        existing_db_model
    )  # Verifica se o refresh foi chamado no objeto correto
    repository.get_by_id.assert_called_once_with(
        1
    )  # Verifica se get_by_id foi chamado no final


def test_update_search_config_not_found():
    db_mock = MagicMock()
    repository = SearchConfigRepository(db_mock)

    # Configura o mock para .first() retornar None, simulando que o SearchConfig não foi encontrado
    db_mock.query.return_value.filter.return_value.first.return_value = None

    update_entity = SearchConfigEntity.SearchConfig(
        search_term="Non Existent",
        is_active=True,
        frequency_days=1,
        preferred_time=time(10, 0),
        user_id=1,
    )

    result = repository.update(999, update_entity)

    # Asserts
    assert result is None
    db_mock.query.assert_called_once()
    db_mock.commit.assert_not_called()  # Não deve comitar se não encontrou
    db_mock.refresh.assert_not_called()  # Não deve fazer refresh se não encontrou
