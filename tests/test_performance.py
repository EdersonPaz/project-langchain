"""
Testes de performance e carga.
"""

import pytest
import time
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabasePerformance:
    """Testes de performance do banco de dados."""
    
    def test_insert_performance(self, db_connection, performance_config):
        """Testa performance de inserção de mensagens."""
        cursor = db_connection.cursor()
        
        start_time = time.time()
        
        # Inserir 100 mensagens
        for i in range(100):
            cursor.execute(
                "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
                (f"session_{i % 10}", "human" if i % 2 == 0 else "ai", f"Mensagem {i}")
            )
        
        db_connection.commit()
        elapsed = time.time() - start_time
        
        # Deve completar em menos de 1 segundo
        assert elapsed < 1.0, f"Inserção muito lenta: {elapsed:.2f}s"
    
    def test_query_performance(self, db_connection, performance_config):
        """Testa performance de queries."""
        cursor = db_connection.cursor()
        
        # Inserir dados
        for i in range(1000):
            cursor.execute(
                "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
                (f"session_{i % 100}", "human", f"Mensagem {i}")
            )
        db_connection.commit()
        
        # Testar performance de query
        start_time = time.time()
        
        for i in range(100):
            cursor.execute(
                "SELECT * FROM message_store WHERE session_id = ? ORDER BY created_at",
                (f"session_{i % 100}",)
            )
            cursor.fetchall()
        
        elapsed = time.time() - start_time
        
        # 100 queries devem ser rápidas
        avg_query_time = elapsed / 100
        assert avg_query_time < performance_config["max_db_query_time"], \
            f"Query muito lenta: {avg_query_time:.4f}s"
    
    def test_database_size(self, db_connection):
        """Testa crescimento do banco de dados."""
        cursor = db_connection.cursor()
        
        # Inserir 10000 mensagens
        for i in range(10000):
            cursor.execute(
                "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
                (f"session_{i % 100}", "human", f"X" * 100 + f" {i}")  # Simular mensagens grandes
            )
        
        db_connection.commit()
        
        # Verificar contador
        cursor.execute("SELECT COUNT(*) FROM message_store")
        count = cursor.fetchone()[0]
        assert count == 10000


class TestMemoryUsage:
    """Testes de uso de memória."""
    
    def test_history_memory_footprint(self):
        """Testa tamanho da conversa em memória."""
        import sys
        
        # Simular histórico
        history = []
        message_size = sys.getsizeof("This is a test message")
        
        for i in range(1000):
            history.append({
                "role": "human" if i % 2 == 0 else "ai",
                "content": f"Message {i}" * 10
            })
        
        total_size = sys.getsizeof(history)
        
        # Histórico de 1000 mensagens não deve ocupar >10MB
        assert total_size < 10 * 1024 * 1024
    
    def test_large_response_handling(self):
        """Testa processamento de respostas grandes."""
        # Simular resposta grande (10KB)
        large_response = "X" * (10 * 1024)
        
        # Deve estar em memória sem problema
        assert len(large_response) == 10240


class TestResponseTime:
    """Testes de tempo de resposta."""
    
    @patch('app.ChatOpenAI')
    def test_chain_invocation_speed(self, mock_openai, temp_env, performance_config):
        """Testa velocidade de invocação da chain."""
        # Setup
        mock_response = Mock(content="Resposta teste")
        mock_openai.return_value = MagicMock()
        mock_openai.return_value.invoke = Mock(return_value=mock_response)
        
        from app import criar_chain
        
        chain = criar_chain(retriever=None)
        
        # Simular invocação
        start_time = time.time()
        
        # Mock da invocação (sem esperar OpenAI real)
        result = mock_openai.return_value.invoke({"input": "Teste"})
        
        elapsed = time.time() - start_time
        
        # Mock deve ser instantâneo
        assert elapsed < 0.1
    
    def test_rag_retrieval_speed(self, mock_retriever):
        """Testa velocidade de recuperação RAG."""
        start_time = time.time()
        
        # Invocar retriever
        docs = mock_retriever.invoke("Teste")
        
        elapsed = time.time() - start_time
        
        # Mock deve ser muito rápido
        assert elapsed < 0.01


class TestConcurrency:
    """Testes de concorrência."""
    
    def test_concurrent_database_writes(self, db_connection):
        """Testa escritas simultâneas no banco."""
        import threading
        import sqlite3

        db_path = db_connection.execute("PRAGMA database_list").fetchone()[2]

        def write_messages(session_id, count):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            for i in range(count):
                cursor.execute(
                    "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
                    (session_id, "human", f"Mensagem {i}")
                )
            conn.commit()
            conn.close()

        # Criar threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=write_messages, args=(f"session_{i}", 100))
            threads.append(t)
            t.start()

        # Esperar conclusão
        for t in threads:
            t.join()

        # Verificar dados
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM message_store")
        count = cursor.fetchone()[0]

        assert count == 500  # 5 threads * 100 messages
    
    def test_multiple_sessions_concurrent(self, db_connection):
        """Testa acesso simultâneo a múltiplas sessões."""
        import threading
        import sqlite3

        db_path = db_connection.execute("PRAGMA database_list").fetchone()[2]

        def access_session(session_id):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            for i in range(50):
                cursor.execute(
                    "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
                    (session_id, "human", f"Msg")
                )
            conn.commit()
            conn.close()

        # 20 threads acessando sessões diferentes
        threads = []
        for i in range(20):
            t = threading.Thread(target=access_session, args=(f"concurrent_session_{i}",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM message_store")
        distinct_sessions = cursor.fetchone()[0]

        assert distinct_sessions == 20


class TestThroughput:
    """Testes de throughput (quantidade de mensagens processadas)."""
    
    def test_database_throughput(self, db_connection):
        """Testa número de mensagens inseridas por segundo."""
        cursor = db_connection.cursor()
        
        start_time = time.time()
        
        # Inserir 1000 mensagens
        for i in range(1000):
            cursor.execute(
                "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
                ("perf_session", "human" if i % 2 == 0 else "ai", f"Msg {i}")
            )
        
        db_connection.commit()
        elapsed = time.time() - start_time
        
        throughput = 1000 / elapsed
        
        # Deve processar pelo menos 500 msg/segundo
        assert throughput > 500
        print(f"Throughput: {throughput:.0f} mensagens/segundo")


class TestScalability:
    """Testes de escalabilidade."""
    
    def test_large_session_history(self, db_connection):
        """Testa com histórico muito grande (1 ano de conversas)."""
        cursor = db_connection.cursor()
        
        # ~365 dias * 100 mensagens/dia = 36500 mensagens
        for i in range(36500):
            cursor.execute(
                "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
                ("long_session", "human" if i % 2 == 0 else "ai", f"Mensagem do dia {i // 100}")
            )
        
        db_connection.commit()
        
        # Deve conseguir recuperar todas
        cursor.execute(
            "SELECT COUNT(*) FROM message_store WHERE session_id = 'long_session'"
        )
        count = cursor.fetchone()[0]
        assert count == 36500
    
    def test_retrieve_large_history_performance(self, db_connection, performance_config):
        """Testa performance de recuperação de histórico grande."""
        cursor = db_connection.cursor()
        
        # Inserir 10000 mensagens
        for i in range(10000):
            cursor.execute(
                "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
                ("large_session", "human" if i % 2 == 0 else "ai", f"Msg")
            )
        
        db_connection.commit()
        
        # Recuperar
        start_time = time.time()
        
        cursor.execute(
            "SELECT * FROM message_store WHERE session_id = 'large_session' ORDER BY created_at"
        )
        rows = cursor.fetchall()
        
        elapsed = time.time() - start_time
        
        assert len(rows) == 10000
        # Recuperar 10000 mensagens em menos de 1 segundo
        assert elapsed < 1.0


class TestResourceOptimization:
    """Testes de otimização de recursos."""
    
    def test_connection_reuse(self, db_connection):
        """Testa reuso de conexão."""
        cursor1 = db_connection.cursor()
        cursor2 = db_connection.cursor()
        
        # Deve compartilhar conexão
        cursor1.execute("INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)", ("test", "human", "m1"))
        cursor2.execute("SELECT COUNT(*) FROM message_store WHERE message_content = 'm1'")
        
        # Cursor2 deve ver inserção do cursor1
        count = cursor2.fetchone()[0]
        assert count >= 1
    
    def test_batch_operations(self, db_connection):
        """Testa operações em batch."""
        cursor = db_connection.cursor()
        
        # Batch de 100
        batch_size = 100
        batches = 10
        
        start_time = time.time()
        
        for batch in range(batches):
            data = [
                (f"batch_session", "human" if i % 2 == 0 else "ai", f"Msg {i}")
                for i in range(batch * batch_size, (batch + 1) * batch_size)
            ]
            cursor.executemany(
                "INSERT INTO message_store (session_id, message_type, message_content) VALUES (?, ?, ?)",
                data
            )
        
        db_connection.commit()
        elapsed = time.time() - start_time
        
        # Batch deve ser rápido (< 0.5s para 1000 inserts)
        assert elapsed < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
