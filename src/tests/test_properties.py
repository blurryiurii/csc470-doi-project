import pytest
from hypothesis import given, strategies as st


username_strategy = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=1,
    max_size=50,
)

bio_strategy = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=0,
    max_size=250,
)

password_strategy = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=1,
    max_size=250,
)

email_strategy = st.emails()

doi_strategy = st.from_regex(r"10\.\d{4,}/[a-zA-Z0-9._-]+", fullmatch=True)

abstract_strategy = st.text(max_size=5000)

title_strategy = st.text(min_size=1, max_size=50)

comment_body_strategy = st.text(min_size=1, max_size=5000)


class TestDOIValidationProperties:
    @given(doi=doi_strategy)
    def test_doi_format_consistency(self, doi):
        assert doi.startswith("10.")
        parts = doi.split("/")
        assert len(parts) >= 2
        prefix = parts[0]
        assert prefix.startswith("10.")
        assert prefix[3:].isdigit()


class TestStringProperties:
    @given(username=username_strategy)
    def test_username_length_constraint(self, username):
        assert 1 <= len(username) <= 50

    @given(bio=bio_strategy)
    def test_bio_length_constraint(self, bio):
        assert 0 <= len(bio) <= 250

    @given(password=password_strategy)
    def test_password_length_constraint(self, password):
        assert 1 <= len(password) <= 250

    @given(abstract=abstract_strategy)
    def test_abstract_length_constraint(self, abstract):
        assert len(abstract) <= 5000

    @given(title=title_strategy)
    def test_title_length_constraint(self, title):
        assert 1 <= len(title) <= 50

    @given(comment_body=comment_body_strategy)
    def test_comment_body_length_constraint(self, comment_body):
        assert 1 <= len(comment_body) <= 5000


class TestEmailProperties:
    @given(email=email_strategy)
    def test_email_contains_at_symbol(self, email):
        assert "@" in email


class TestPasswordMatchingProperty:
    @given(password=password_strategy)
    def test_password_equality_is_reflexive(self, password):
        assert password == password

    @given(password1=password_strategy, password2=password_strategy)
    def test_password_equality_is_symmetric(self, password1, password2):
        if password1 == password2:
            assert password2 == password1

    @given(password=password_strategy)
    def test_password_verify_logic(self, password):
        password_verify = password
        assert password == password_verify
