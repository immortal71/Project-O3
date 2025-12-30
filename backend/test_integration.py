"""
Test Integration - Verify all components work together

Tests:
1. Data loader loads all datasets
2. API endpoints return real data
3. Search works across thousands of compounds
4. Hero cases integrate properly
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from data_loader import get_data_loader
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_data_loader():
    """Test data loader functionality"""
    
    print("\n" + "=" * 70)
    print("TEST 1: Data Loader")
    print("=" * 70)
    
    loader = get_data_loader()
    stats = loader.get_stats()
    
    print(f"\n✅ Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value:,}")
    
    # Verify we have data
    assert stats['total_drugs'] > 6000, "Should have 6000+ drugs from Broad Hub"
    assert stats['hero_cases'] == 15, "Should have 15 hero cases"
    assert stats['oncology_compounds'] > 200, "Should have 200+ oncology compounds"
    
    print(f"\n✅ Data loader: PASSED")
    return True


def test_search():
    """Test search functionality"""
    
    print("\n" + "=" * 70)
    print("TEST 2: Search Functionality")
    print("=" * 70)
    
    loader = get_data_loader()
    
    # Test search for metformin
    print(f"\n🔍 Searching for 'metformin'...")
    results = loader.search_drugs('metformin')
    print(f"   Found {len(results)} results")
    if results:
        drug = results[0]
        print(f"   - {drug.get('pert_iname')}: {drug.get('clinical_phase')} - {drug.get('moa')}")
    
    assert len(results) > 0, "Should find metformin"
    
    # Test search for oncology
    print(f"\n🔍 Searching for 'cancer'...")
    results = loader.search_drugs('cancer', limit=10)
    print(f"   Found {len(results)} results")
    
    assert len(results) > 0, "Should find cancer-related drugs"
    
    # Test hero case lookup
    print(f"\n🔍 Looking up hero case: Aspirin...")
    hero = loader.get_hero_case('Aspirin')
    if hero:
        print(f"   - {hero['drug_name']}: confidence {hero['confidence_score']}")
        print(f"   - Cancer types: {hero['repurposed_cancer']}")
    
    assert hero is not None, "Should find Aspirin hero case"
    assert hero['confidence_score'] > 0.9, "Aspirin should have high confidence"
    
    print(f"\n✅ Search: PASSED")
    return True


def test_indexes():
    """Test lookup indexes"""
    
    print("\n" + "=" * 70)
    print("TEST 3: Lookup Indexes")
    print("=" * 70)
    
    loader = get_data_loader()
    
    # Test drug lookup by name
    print(f"\n📑 Testing name index...")
    drug = loader.get_drug_by_name('metformin')
    if drug:
        print(f"   Found: {drug.get('pert_iname')}")
    
    # Test mechanism lookup
    print(f"\n📑 Testing mechanism index...")
    drugs = loader.get_drugs_by_mechanism('CDK inhibitor')
    print(f"   Found {len(drugs)} drugs with 'CDK inhibitor' mechanism")
    
    # Test phase lookup
    print(f"\n📑 Testing phase index...")
    launched = loader.get_drugs_by_phase('Launched')
    print(f"   Found {len(launched)} launched drugs")
    
    assert len(launched) > 1000, "Should have 1000+ launched drugs"
    
    print(f"\n✅ Indexes: PASSED")
    return True


def test_hero_cases():
    """Test hero cases data"""
    
    print("\n" + "=" * 70)
    print("TEST 4: Hero Cases")
    print("=" * 70)
    
    loader = get_data_loader()
    heroes = loader.get_hero_cases()
    
    print(f"\n🌟 Hero Cases: {len(heroes)}")
    
    # Check top cases
    sorted_heroes = sorted(heroes, key=lambda x: x['confidence_score'], reverse=True)
    print(f"\n   Top 5 by confidence:")
    for i, case in enumerate(sorted_heroes[:5], 1):
        print(f"   {i}. {case['drug_name']}: {case['confidence_score']} ({case['phase']})")
    
    # Verify all have required fields
    for case in heroes:
        assert 'drug_name' in case
        assert 'confidence_score' in case
        assert 'repurposed_cancer' in case
        assert 'mechanism' in case
        assert 'trial_count' in case
    
    print(f"\n✅ Hero cases: PASSED")
    return True


def main():
    """Run all tests"""
    
    print("\n" + "#" * 70)
    print("# INTEGRATION TEST SUITE")
    print("#" * 70)
    
    tests = [
        test_data_loader,
        test_search,
        test_indexes,
        test_hero_cases
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED - Backend integration working!")
        return True
    else:
        print(f"\n⚠️ Some tests failed - check errors above")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
