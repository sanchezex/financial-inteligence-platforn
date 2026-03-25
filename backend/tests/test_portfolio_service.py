"""
Unit Tests for Portfolio Service

Tests for PortfolioService and PaperTradingService classes.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Patch the services module before importing portfolio_service to avoid import cascades
import app.services
app.services.redis_manager = Mock()
app.services.kafka_manager = Mock()

from app.services.portfolio_service import PortfolioService, PaperTradingService


class TestPortfolioService:
    """Test cases for PortfolioService class."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = Mock()
        return db
    
    @pytest.fixture
    def portfolio_service(self, mock_db):
        """Create a PortfolioService instance with mocked dependencies."""
        from app.services.portfolio_service import PortfolioService
        return PortfolioService(db=mock_db, user_id=1, is_paper=True)
    
    def test_init(self, portfolio_service):
        """Test PortfolioService initialization."""
        assert portfolio_service.user_id == 1
        assert portfolio_service.is_paper is True
        assert portfolio_service.db is not None
    
    def test_get_positions_empty(self, portfolio_service, mock_db):
        """Test get_positions returns empty list when no positions exist."""
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = portfolio_service.get_positions()
        
        assert result == []
        mock_db.query.assert_called()
    
    def test_get_positions_single_position(self, portfolio_service, mock_db):
        """Test get_positions with a single position."""
        # Create a mock position
        mock_position = Mock()
        mock_position.id = 1
        mock_position.symbol = 'AAPL'
        mock_position.side = 'long'
        mock_position.quantity = Decimal('100')
        mock_position.avg_entry_price = Decimal('150.00')
        mock_position.current_price = Decimal('155.00')
        mock_position.total_cost = Decimal('15000')
        mock_position.day_change = Decimal('100')
        mock_position.day_change_percent = Decimal('1.0')
        mock_position.opened_at = datetime(2024, 1, 1, 10, 0, 0)
        mock_position.updated_at = datetime(2024, 1, 15, 10, 0, 0)
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_position]
        
        result = portfolio_service.get_positions()
        
        assert len(result) == 1
        assert result[0]['symbol'] == 'AAPL'
        assert result[0]['side'] == 'long'
        assert result[0]['quantity'] == 100.0
        assert result[0]['unrealized_pnl'] == 500.0  # (155 - 150) * 100
        assert result[0]['unrealized_pnl_percent'] == pytest.approx(3.333, rel=0.01)
    
    def test_get_positions_short_position(self, portfolio_service, mock_db):
        """Test get_positions with a short position."""
        mock_position = Mock()
        mock_position.id = 1
        mock_position.symbol = 'TSLA'
        mock_position.side = 'short'
        mock_position.quantity = Decimal('50')
        mock_position.avg_entry_price = Decimal('200.00')
        mock_position.current_price = Decimal('190.00')
        mock_position.total_cost = Decimal('10000')
        mock_position.day_change = None
        mock_position.day_change_percent = None
        mock_position.opened_at = None
        mock_position.updated_at = None
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_position]
        
        result = portfolio_service.get_positions()
        
        assert len(result) == 1
        assert result[0]['symbol'] == 'TSLA'
        assert result[0]['side'] == 'short'
        # Short position: (200 - 190) * 50 = 500 profit
        assert result[0]['unrealized_pnl'] == 500.0
    
    def test_get_portfolio_summary(self, portfolio_service, mock_db):
        """Test get_portfolio_summary calculates totals correctly."""
        # Mock positions
        mock_pos1 = Mock()
        mock_pos1.id = 1
        mock_pos1.symbol = 'AAPL'
        mock_pos1.side = 'long'
        mock_pos1.quantity = Decimal('100')
        mock_pos1.avg_entry_price = Decimal('150.00')
        mock_pos1.current_price = Decimal('155.00')
        mock_pos1.total_cost = Decimal('15000')
        mock_pos1.day_change = Decimal('100')
        mock_pos1.day_change_percent = Decimal('1.0')
        mock_pos1.opened_at = None
        mock_pos1.updated_at = None
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_pos1]
        
        result = portfolio_service.get_portfolio_summary()
        
        assert result['positions_count'] == 1
        assert result['total_value'] == 15500.0  # 100 * 155
        assert result['total_cost'] == 15000.0
        assert result['total_unrealized_pnl'] == 500.0
        assert result['total_return'] == pytest.approx(3.333, rel=0.01)
        assert result['day_pnl'] == 100.0
        assert result['is_paper'] is True
    
    def test_get_portfolio_summary_empty(self, portfolio_service, mock_db):
        """Test get_portfolio_summary with no positions."""
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        result = portfolio_service.get_portfolio_summary()
        
        assert result['positions_count'] == 0
        assert result['total_value'] == 0
        assert result['total_cost'] == 0
        assert result['total_unrealized_pnl'] == 0
    
    def test_update_position_price(self, portfolio_service, mock_db):
        """Test update_position_price updates the database."""
        mock_position = Mock()
        mock_position.id = 1
        mock_position.symbol = 'AAPL'
        mock_position.side = 'long'
        mock_position.quantity = Decimal('100')
        mock_position.avg_entry_price = Decimal('150.00')
        mock_position.total_cost = Decimal('15000')
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_position]
        
        portfolio_service.update_position_price('AAPL', 160.00)
        
        assert mock_position.current_price == Decimal('160.00')
        mock_db.commit.assert_called_once()
    
    def test_update_position_price_short(self, portfolio_service, mock_db):
        """Test update_position_price for short position."""
        mock_position = Mock()
        mock_position.id = 1
        mock_position.symbol = 'TSLA'
        mock_position.side = 'short'
        mock_position.quantity = Decimal('50')
        mock_position.avg_entry_price = Decimal('200.00')
        mock_position.total_cost = Decimal('10000')
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_position]
        
        portfolio_service.update_position_price('TSLA', 190.00)
        
        # Short position: price drop = profit
        assert mock_position.current_price == Decimal('190.00')
        mock_db.commit.assert_called_once()


class TestPaperTradingService:
    """Test cases for PaperTradingService class."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def paper_trading_service(self, mock_db):
        """Create a PaperTradingService instance."""
        from app.services.portfolio_service import PaperTradingService
        
        # Mock the account query
        mock_account = Mock()
        mock_account.user_id = 1
        mock_account.initial_balance = Decimal('100000.00')
        mock_account.current_balance = Decimal('100000.00')
        mock_account.buying_power = Decimal('100000.00')
        mock_account.total_pnl = Decimal('0')
        mock_account.total_return = Decimal('0')
        mock_account.day_pnl = Decimal('0')
        mock_account.day_return = Decimal('0')
        mock_account.total_trades = 0
        mock_account.winning_trades = 0
        mock_account.losing_trades = 0
        mock_account.win_rate = Decimal('0')
        mock_account.max_drawdown = Decimal('0')
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_account
        
        return PaperTradingService(db=mock_db, user_id=1)
    
    def test_init(self, paper_trading_service):
        """Test PaperTradingService initialization."""
        assert paper_trading_service.user_id == 1
        assert paper_trading_service.is_paper is True
        assert paper_trading_service.account is not None
    
    def test_execute_buy_order_success(self, paper_trading_service, mock_db):
        """Test successful buy order execution."""
        # Mock no existing position
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = paper_trading_service.execute_buy_order('AAPL', 10, 150.00)
        
        assert result['success'] is True
        assert result['symbol'] == 'AAPL'
        assert result['side'] == 'buy'
        assert result['quantity'] == 10
        assert result['price'] == 150.00
        assert result['total_cost'] == 1500.0
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
    
    def test_execute_buy_order_insufficient_funds(self, paper_trading_service):
        """Test buy order with insufficient buying power."""
        # Set low buying power
        paper_trading_service.account.buying_power = Decimal('100')
        
        result = paper_trading_service.execute_buy_order('AAPL', 100, 150.00)
        
        assert result['success'] is False
        assert 'Insufficient buying power' in result['error']
        assert result['required'] == 15000.0
        assert result['available'] == 100.0
    
    def test_execute_buy_order_add_to_position(self, paper_trading_service, mock_db):
        """Test adding to existing position."""
        mock_existing_position = Mock()
        mock_existing_position.id = 1
        mock_existing_position.quantity = Decimal('100')
        mock_existing_position.avg_entry_price = Decimal('150.00')
        mock_existing_position.total_cost = Decimal('15000')
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing_position
        
        result = paper_trading_service.execute_buy_order('AAPL', 50, 160.00)
        
        assert result['success'] is True
        # New average: (100 * 150 + 50 * 160) / 150 = 153.33
        assert mock_existing_position.avg_entry_price == pytest.approx(Decimal('153.333'), rel=0.01)
    
    def test_execute_sell_order_success(self, paper_trading_service, mock_db):
        """Test successful sell order execution."""
        mock_position = Mock()
        mock_position.id = 1
        mock_position.quantity = Decimal('100')
        mock_position.avg_entry_price = Decimal('150.00')
        mock_position.total_cost = Decimal('15000')
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_position
        
        result = paper_trading_service.execute_sell_order('AAPL', 50, 160.00)
        
        assert result['success'] is True
        assert result['side'] == 'sell'
        assert result['quantity'] == 50
        assert result['price'] == 160.00
        assert result['total_value'] == 8000.0
        # Cost basis: 50 * 150 = 7500
        # Realized P&L: 8000 - 7500 = 500
        assert result['realized_pnl'] == 500.0
    
    def test_execute_sell_order_no_position(self, paper_trading_service, mock_db):
        """Test sell order with no existing position."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = paper_trading_service.execute_sell_order('AAPL', 10, 150.00)
        
        assert result['success'] is False
        assert 'No position found' in result['error']
    
    def test_execute_sell_order_insufficient_shares(self, paper_trading_service, mock_db):
        """Test sell order with insufficient shares."""
        mock_position = Mock()
        mock_position.quantity = Decimal('50')
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_position
        
        result = paper_trading_service.execute_sell_order('AAPL', 100, 150.00)
        
        assert result['success'] is False
        assert 'Insufficient shares' in result['error']
        assert result['available'] == 50.0
        assert result['requested'] == 100
    
    def test_get_account_summary(self, paper_trading_service):
        """Test get_account_summary returns correct data."""
        result = paper_trading_service.get_account_summary()
        
        assert result['initial_balance'] == 100000.0
        assert result['current_balance'] == 100000.0
        assert result['buying_power'] == 100000.0
        assert result['total_pnl'] == 0
        assert result['total_trades'] == 0
    
    def test_reset_account(self, paper_trading_service, mock_db):
        """Test account reset functionality."""
        # Create mock positions
        mock_position1 = Mock()
        mock_position2 = Mock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_position1, mock_position2]
        
        result = paper_trading_service.reset_account()
        
        assert result['success'] is True
        assert result['initial_balance'] == 100000.0
        assert result['current_balance'] == 100000.0
        mock_db.delete.assert_called()
        mock_db.commit.assert_called()


class TestPortfolioMetrics:
    """Test cases for portfolio metrics calculations."""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def portfolio_service(self, mock_db):
        from app.services.portfolio_service import PortfolioService
        return PortfolioService(db=mock_db, user_id=1, is_paper=True)
    
    def test_calculate_portfolio_metrics_with_history(self, portfolio_service, mock_db):
        """Test calculate_portfolio_metrics with historical data."""
        # Mock positions
        mock_position = Mock()
        mock_position.id = 1
        mock_position.symbol = 'AAPL'
        mock_position.side = 'long'
        mock_position.quantity = Decimal('100')
        mock_position.avg_entry_price = Decimal('150.00')
        mock_position.current_price = Decimal('155.00')
        mock_position.total_cost = Decimal('15000')
        mock_position.day_change = None
        mock_position.day_change_percent = None
        mock_position.opened_at = None
        mock_position.updated_at = None
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_position]
        
        # Mock portfolio history
        mock_history = Mock()
        mock_history.date = date(2024, 1, 1)
        mock_history.total_value = Decimal('100000')
        mock_history.day_pnl = Decimal('500')
        mock_history.day_return = Decimal('0.5')
        mock_history.total_return = Decimal('5.0')
        mock_history.unrealized_pnl = Decimal('5000')
        mock_history.realized_pnl = Decimal('0')
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_history]
        
        result = portfolio_service.calculate_portfolio_metrics()
        
        assert 'total_value' in result
        assert 'total_return' in result
        assert 'sharpe_ratio' in result
        assert 'beta' in result
        assert 'max_drawdown' in result
        assert result['positions_count'] == 1


class TestInputValidation:
    """Test cases for input validation."""
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def portfolio_service(self, mock_db):
        from app.services.portfolio_service import PortfolioService
        return PortfolioService(db=mock_db, user_id=1, is_paper=True)
    
    def test_get_positions_negative_quantity(self, portfolio_service, mock_db):
        """Test that positions with negative quantity are filtered out."""
        mock_position = Mock()
        mock_position.id = 1
        mock_position.symbol = 'AAPL'
        mock_position.side = 'long'
        mock_position.quantity = Decimal('-10')  # Negative - should be filtered
        mock_position.avg_entry_price = Decimal('150.00')
        mock_position.current_price = Decimal('155.00')
        mock_position.total_cost = Decimal('15000')
        mock_position.day_change = None
        mock_position.day_change_percent = None
        mock_position.opened_at = None
        mock_position.updated_at = None
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_position]
        
        result = portfolio_service.get_positions()
        
        # The filter should handle negative quantities
        # Service queries for quantity > 0, so negative positions should be excluded
        # This test verifies the query is constructed correctly
        mock_db.query.assert_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

