#!/usr/bin/env python3
"""
Test script for Hospital Management System Home Page Enhancement
"""

import urllib.request
import urllib.error
import sys

BASE = "http://127.0.0.1:8000"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib.request.HTTPError(req.get_full_url(), code, msg, headers, fp)

opener = urllib.request.build_opener(NoRedirectHandler())
urllib.request.install_opener(opener)

def test_url(path, expect_redirect=False):
    """Test a URL and return status info"""
    try:
        response = urllib.request.urlopen(f"{BASE}{path}")
        status = response.getcode()
        return {"path": path, "status": status, "ok": True, "redirect": False}
    except urllib.error.HTTPError as e:
        if e.code == 302:
            return {"path": path, "status": 302, "ok": True, "redirect": True, "location": e.headers.get('Location', '')}
        return {"path": path, "status": e.code, "ok": False, "redirect": False, "error": e.reason}
    except Exception as e:
        return {"path": path, "status": None, "ok": False, "redirect": False, "error": str(e)}

def test_home_content():
    """Verify home page HTML contains all expected elements"""
    try:
        response = urllib.request.urlopen(f"{BASE}/")
        html = response.read().decode('utf-8', errors='replace')
        
        checks = [
            ("Hero title", "Hospital Management System" in html),
            ("Hero tagline", "Complete Healthcare Solution" in html),
            ("Quick Actions heading", "Quick Actions" in html),
            ("Add Patient button", "Add Patient" in html and "feature-patient" in html),
            ("Add Doctor button", "Add Doctor" in html and "feature-doctor" in html),
            ("Add Room button", "Add Room" in html and "feature-room" in html),
            ("Add Appointment button", "Add Appointment" in html and "feature-appointment" in html),
            ("Add Operation button", "Add Operation" in html and "feature-operation" in html),
            ("View Beds button", "View Beds" in html and "feature-bed" in html),
            ("Add Treatment button", "Add Treatment" in html and "feature-treatment" in html),
            ("Add Lab Test button", "Add Lab Test" in html and "feature-lab" in html),
            ("Add Invoice button", "Add Invoice" in html and "feature-invoice" in html),
            ("View Patients button", "View Patients" in html and "feature-list" in html),
            ("View Doctors button", "View Doctors" in html and "feature-list-doctor" in html),
            ("Reports button", "Reports" in html and "feature-reports" in html),
            ("Doctor Portal dropdown", "Doctor Portal" in html),
            ("Patient Portal dropdown", "Patient Portal" in html),
            ("Admin Portal dropdown", "Admin Portal" in html),
            ("Guest info section", "Why Choose Us" in html),
            ("Dashboard preserved", "Hospital Dashboard" in html),
            ("Stats present", "total_doctors" in html),
            ("Charts present", "revenueChart" in html),
            ("CSS style.css linked", "style.css" in html),
        ]
        
        passed = 0
        failed = 0
        for label, result in checks:
            status = "PASS" if result else "FAIL"
            if result:
                passed += 1
            else:
                failed += 1
                print(f"  {status}: {label}")
        
        print(f"\n  Content checks: {passed}/{len(checks)} passed")
        return failed == 0, html
        
    except Exception as e:
        print(f"  FAIL: Could not fetch home page - {e}")
        return False, ""

def main():
    print("=" * 60)
    print("HOSPITAL MANAGEMENT SYSTEM - HOMEPAGE TEST SUITE")
    print("=" * 60)
    
    # Test 1: Home page content
    print("\n--- TEST 1: Home Page Content Verification ---")
    home_ok, html = test_home_content()
    
    # Test 2: Button URL paths
    print("\n--- TEST 2: Feature Button URL Path Verification ---")
    button_urls = [
        "/",  # Home
        "/login/",  # Login
        "/register/",  # Register
        # Feature add pages
        "/patients/add/",  # Add Patient
        "/doctors/add/",  # Add Doctor
        "/rooms/add/",  # Add Room
        "/appointments/add/",  # Add Appointment
        "/operations/add/",  # Add Operation
        "/beds/",  # View Beds
        "/treatments/add/",  # Add Treatment
        "/lab-tests/add/",  # Add Lab Test
        "/invoices/add/",  # Add Invoice
        # View pages
        "/patients/",  # View Patients
        "/doctors/",  # View Doctors
        "/reports/",  # Reports
    ]
    
    all_ok = True
    for url in button_urls:
        result = test_url(url)
        if not result["ok"]:
            all_ok = False
            print(f"  FAIL: {url} -> {result['status']} ({result.get('error', 'N/A')})")
        elif result.get("redirect"):
            print(f"  OK:   {url} -> 302 redirect to {result.get('location', 'login')}")
        else:
            print(f"  OK:   {url} -> {result['status']}")
    
    # Test 3: CSS file
    print("\n--- TEST 3: Static CSS File Verification ---")
    css_result = test_url("/static/css/style.css")
    if css_result["ok"] and not css_result.get("redirect"):
        print(f"  OK:   /static/css/style.css -> {css_result['status']}")
    else:
        print(f"  FAIL: /static/css/style.css -> {css_result.get('status', 'N/A')}")
        all_ok = False
    
    # Test 4: Check new CSS classes exist in file
    print("\n--- TEST 4: CSS Class Verification ---")
    try:
        css_resp = urllib.request.urlopen(f"{BASE}/static/css/style.css")
        css_content = css_resp.read().decode('utf-8', errors='replace')
        css_classes = [
            ".hero-section", ".feature-card", ".dropdown-menu", 
            ".dropdown-toggle", ".btn-doctor", ".btn-patient", ".btn-admin",
            ".role-badge", ".today-stats", ".features-grid",
            ".info-card", ".stats-grid", "slideDown"
        ]
        missing = []
        for cls in css_classes:
            if cls not in css_content:
                missing.append(cls)
        if missing:
            print(f"  FAIL: Missing CSS classes: {', '.join(missing)}")
            all_ok = False
        else:
            print(f"  OK:   All {len(css_classes)} new CSS classes found in style.css")
    except Exception as e:
        print(f"  FAIL: Could not verify CSS classes - {e}")
        all_ok = False
    
    # Test 5: Chart API
    print("\n--- TEST 5: Chart Data API ---")
    chart_result = test_url("/api/chart-data/")
    if chart_result["ok"] and not chart_result.get("redirect"):
        print(f"  OK:   /api/chart-data/ -> {chart_result['status']}")
    else:
        print(f"  WARN: /api/chart-data/ -> {chart_result.get('status', 'N/A')} (may need auth)")
    
    # Summary
    print("\n" + "=" * 60)
    if home_ok and all_ok:
        print("RESULT: ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("RESULT: SOME TESTS FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
