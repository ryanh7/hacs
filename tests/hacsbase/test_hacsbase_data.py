"""Data Test Suite."""
from unittest.mock import patch

from custom_components.hacs.base import HacsRepositories
from custom_components.hacs.enums import HacsGitHubRepo
from custom_components.hacs.utils.data import HacsData


async def test_hacs_data_async_write1(hacs, repository):
    data = HacsData(hacs)
    repository.data.installed = True
    repository.data.installed_version = "1"
    hacs.repositories.register(repository)
    await data.async_write()


async def test_hacs_data_async_write2(hacs):
    data = HacsData(hacs)
    hacs.system.disabled_reason = None
    hacs.repositories = HacsRepositories()
    await data.async_write()


async def test_hacs_data_restore_write_not_new(hacs, caplog):
    data = HacsData(hacs)

    async def _mocked_loads(hass, key):
        if key == "repositories":
            return {
                "1727333146": {
                    "category": "integration",
                    "full_name": "hacs/integration2",
                    "installed": True,
                    "show_beta": True,
                },
                "202226247": {
                    "category": "integration",
                    "full_name": "shbatm/hacs-isy994",
                    "installed": False,
                },
            }
        elif key == "hacs":
            return {}
        elif key == "data":
            return {}
        elif key == "renamed_repositories":
            return {}
        else:
            raise ValueError(f"No mock for {key}")

    with patch("os.path.exists", return_value=True), patch(
        "custom_components.hacs.utils.data.async_load_from_store",
        side_effect=_mocked_loads,
    ):
        await data.restore()

    assert hacs.repositories.get_by_id("202226247")
    assert hacs.repositories.get_by_full_name("shbatm/hacs-isy994")

    assert hacs.repositories.get_by_id("1727333146")
    assert hacs.repositories.get_by_full_name(HacsGitHubRepo.INTEGRATION)

    assert hacs.repositories.get_by_id("1727333146").data.show_beta is True
    assert hacs.repositories.get_by_id("1727333146").data.installed is True

    with patch("custom_components.hacs.utils.data.async_save_to_store") as mock_async_save_to_store:
        await data.async_write()
    assert mock_async_save_to_store.called
    assert "Loading base repository information" not in caplog.text
