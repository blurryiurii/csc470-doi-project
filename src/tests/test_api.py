import responses
import requests


class TestCrossrefAPI:
    @responses.activate
    def test_check_doi_valid(self):
        doi_valid = "10.1000/valid_doi"
        _ = responses.add(
            responses.GET,
            f"https://api.crossref.org/works/{doi_valid}",
            status=200,
        )

        result = requests.get(f"https://api.crossref.org/works/{doi_valid}")
        assert result.status_code == 200

    @responses.activate
    def test_check_doi_invalid(self):
        doi_invalid = "10.1000/invalid_doi"
        _ = responses.add(
            responses.GET,
            f"https://api.crossref.org/works/{doi_invalid}",
            status=404,
        )

        result = requests.get(f"https://api.crossref.org/works/{doi_invalid}")
        assert result.status_code == 404

    @responses.activate
    def test_check_doi_server_error(self):
        doi_error = "10.1000/server_error"
        _ = responses.add(
            responses.GET,
            f"https://api.crossref.org/works/{doi_error}",
            status=500,
        )

        result = requests.get(f"https://api.crossref.org/works/{doi_error}")
        assert result.status_code == 500

    @responses.activate
    def test_check_doi_special_characters(self):
        doi_special = "10.1234/abc-def_ghi.jkl"
        _ = responses.add(
            responses.GET,
            f"https://api.crossref.org/works/{doi_special}",
            status=200,
        )

        result = requests.get(f"https://api.crossref.org/works/{doi_special}")
        assert result.status_code == 200
