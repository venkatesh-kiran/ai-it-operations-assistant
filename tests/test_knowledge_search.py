from tools.knowledge_search import search_knowledge


def test_tc001_knowledge_search_vpn_password_reset(test_environment):
    """TC-001: VPN password reset is found in the local knowledge base."""
    results = search_knowledge.invoke(
        {"query": "How do I reset my VPN password?"}
    )

    assert results
    assert results[0]["id"] == "KB001"
    assert "Reset Password" in results[0]["content"]
    assert "MFA" in results[0]["content"]


def test_tc007_unsupported_knowledge_request(test_environment):
    """TC-007: Unsupported knowledge returns the explicit no-result marker."""
    results = search_knowledge.invoke(
        {"query": "What is the company's holiday policy?"}
    )

    assert len(results) == 1
    assert results[0]["id"] == "NO_RESULT"
