from src.app.dashboard import build_dashboard_snapshot
from src.config import get_settings
from src.pipelines.common import build_pipeline_artifacts
from src.portfolio.paper_portfolio import PaperPortfolio


def test_dashboard_snapshot_contains_recommendations_and_portfolio(tmp_path) -> None:
    settings = get_settings()
    settings.state_dir = tmp_path
    settings.cache_dir = tmp_path / "cache"
    settings.ensure_dirs()

    artifacts = build_pipeline_artifacts(settings)
    portfolio = PaperPortfolio(settings)
    snapshot = build_dashboard_snapshot(artifacts, portfolio)

    assert "recommendations" in snapshot
    assert "portfolio_metrics" in snapshot
    assert isinstance(snapshot["recommendations"], list)
