#include <unity.h>
#include "FontMath.h"

using namespace pixelpulse;

// ── stringWidth4x6 ──

void test_4x6_empty() {
    TEST_ASSERT_EQUAL(0, stringWidth4x6(""));
}

void test_4x6_single_char() {
    TEST_ASSERT_EQUAL(4, stringWidth4x6("A"));
}

void test_4x6_two_chars() {
    TEST_ASSERT_EQUAL(9, stringWidth4x6("AB")); // 4+1+4
}

void test_4x6_three_chars() {
    TEST_ASSERT_EQUAL(14, stringWidth4x6("ABC")); // 4+1+4+1+4
}

void test_4x6_long_string() {
    // "HELLO FRIEND" = 12 chars → 12*4 + 11*1 = 59
    TEST_ASSERT_EQUAL(59, stringWidth4x6("HELLO FRIEND"));
}

void test_4x6_max_panel_fit() {
    // Panel is 64px. Max chars that fit: (64+1)/(4+1) = 13 chars = 13*4+12 = 64
    TEST_ASSERT_EQUAL(64, stringWidth4x6("1234567890123"));
    // 14 chars = 14*4+13 = 69 > 64, doesn't fit
    TEST_ASSERT_EQUAL(69, stringWidth4x6("12345678901234"));
}

// ── stringWidth6x8 ──

void test_6x8_empty() {
    TEST_ASSERT_EQUAL(0, stringWidth6x8(""));
}

void test_6x8_single_char() {
    TEST_ASSERT_EQUAL(6, stringWidth6x8("A"));
}

void test_6x8_two_chars() {
    TEST_ASSERT_EQUAL(13, stringWidth6x8("AB")); // 6+1+6
}

void test_6x8_long_string() {
    // "HELLO" = 5 chars → 5*6 + 4*1 = 34
    TEST_ASSERT_EQUAL(34, stringWidth6x8("HELLO"));
}

void test_6x8_max_panel_fit() {
    // Panel is 64px. Max chars: (64+1)/(6+1) = 9.28 → 9 chars = 9*6+8 = 62
    TEST_ASSERT_EQUAL(62, stringWidth6x8("123456789"));
    // 10 chars = 10*6+9 = 69 > 64
    TEST_ASSERT_EQUAL(69, stringWidth6x8("1234567890"));
}

// ── centerX ──

void test_center_narrow_string() {
    // 9px string on 64px panel: (64-9)/2 = 27
    TEST_ASSERT_EQUAL(27, centerX(64, 9));
}

void test_center_full_width() {
    TEST_ASSERT_EQUAL(0, centerX(64, 64));
}

void test_center_empty_string() {
    TEST_ASSERT_EQUAL(32, centerX(64, 0));
}

void test_center_wider_than_panel() {
    // 70px string on 64px: (64-70)/2 = -3 (clips left)
    TEST_ASSERT_EQUAL(-3, centerX(64, 70));
}

void test_center_single_pixel() {
    TEST_ASSERT_EQUAL(31, centerX(64, 1));
}

void test_center_odd_width() {
    // 13px on 64px: (64-13)/2 = 25 (integer division rounds down)
    TEST_ASSERT_EQUAL(25, centerX(64, 13));
}

void test_center_32px_panel() {
    // Different panel height for vertical centering
    TEST_ASSERT_EQUAL(11, centerX(32, 9));
}

int main() {
    UNITY_BEGIN();

    RUN_TEST(test_4x6_empty);
    RUN_TEST(test_4x6_single_char);
    RUN_TEST(test_4x6_two_chars);
    RUN_TEST(test_4x6_three_chars);
    RUN_TEST(test_4x6_long_string);
    RUN_TEST(test_4x6_max_panel_fit);

    RUN_TEST(test_6x8_empty);
    RUN_TEST(test_6x8_single_char);
    RUN_TEST(test_6x8_two_chars);
    RUN_TEST(test_6x8_long_string);
    RUN_TEST(test_6x8_max_panel_fit);

    RUN_TEST(test_center_narrow_string);
    RUN_TEST(test_center_full_width);
    RUN_TEST(test_center_empty_string);
    RUN_TEST(test_center_wider_than_panel);
    RUN_TEST(test_center_single_pixel);
    RUN_TEST(test_center_odd_width);
    RUN_TEST(test_center_32px_panel);

    return UNITY_END();
}
