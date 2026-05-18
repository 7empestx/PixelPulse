#include <unity.h>
#include "SpriteData.h"

using namespace pixelpulse;

// ── spriteByteCount ──

void test_byte_count_8x1() {
    TEST_ASSERT_EQUAL(1, spriteByteCount(8, 1));
}

void test_byte_count_8x2() {
    TEST_ASSERT_EQUAL(2, spriteByteCount(8, 2));
}

void test_byte_count_64x32() {
    TEST_ASSERT_EQUAL(256, spriteByteCount(64, 32));
}

void test_byte_count_1x1() {
    TEST_ASSERT_EQUAL(1, spriteByteCount(1, 1));
}

void test_byte_count_non_byte_aligned() {
    // 3x3 = 9 bits → 2 bytes
    TEST_ASSERT_EQUAL(2, spriteByteCount(3, 3));
    // 10x1 = 10 bits → 2 bytes
    TEST_ASSERT_EQUAL(2, spriteByteCount(10, 1));
    // 7x1 = 7 bits → 1 byte
    TEST_ASSERT_EQUAL(1, spriteByteCount(7, 1));
}

// ── spritePixelAt: known pattern ──

static const uint8_t CHECKERBOARD[] = {
    0b10101010, // row 0: pixels at x=0,2,4,6
    0b01010101, // row 1: pixels at x=1,3,5,7
};

void test_pixel_row0_on() {
    TEST_ASSERT_TRUE(spritePixelAt(CHECKERBOARD, 8, 0, 0));
    TEST_ASSERT_TRUE(spritePixelAt(CHECKERBOARD, 8, 2, 0));
    TEST_ASSERT_TRUE(spritePixelAt(CHECKERBOARD, 8, 4, 0));
    TEST_ASSERT_TRUE(spritePixelAt(CHECKERBOARD, 8, 6, 0));
}

void test_pixel_row0_off() {
    TEST_ASSERT_FALSE(spritePixelAt(CHECKERBOARD, 8, 1, 0));
    TEST_ASSERT_FALSE(spritePixelAt(CHECKERBOARD, 8, 3, 0));
    TEST_ASSERT_FALSE(spritePixelAt(CHECKERBOARD, 8, 5, 0));
    TEST_ASSERT_FALSE(spritePixelAt(CHECKERBOARD, 8, 7, 0));
}

void test_pixel_row1_on() {
    TEST_ASSERT_TRUE(spritePixelAt(CHECKERBOARD, 8, 1, 1));
    TEST_ASSERT_TRUE(spritePixelAt(CHECKERBOARD, 8, 3, 1));
    TEST_ASSERT_TRUE(spritePixelAt(CHECKERBOARD, 8, 5, 1));
    TEST_ASSERT_TRUE(spritePixelAt(CHECKERBOARD, 8, 7, 1));
}

void test_pixel_row1_off() {
    TEST_ASSERT_FALSE(spritePixelAt(CHECKERBOARD, 8, 0, 1));
    TEST_ASSERT_FALSE(spritePixelAt(CHECKERBOARD, 8, 2, 1));
    TEST_ASSERT_FALSE(spritePixelAt(CHECKERBOARD, 8, 4, 1));
    TEST_ASSERT_FALSE(spritePixelAt(CHECKERBOARD, 8, 6, 1));
}

// ── spritePixelAt: all zeros ──

static const uint8_t ALL_ZEROS[] = { 0x00, 0x00 };

void test_pixel_all_zeros() {
    for (int x = 0; x < 8; x++) {
        TEST_ASSERT_FALSE(spritePixelAt(ALL_ZEROS, 8, x, 0));
        TEST_ASSERT_FALSE(spritePixelAt(ALL_ZEROS, 8, x, 1));
    }
}

// ── spritePixelAt: all ones ──

static const uint8_t ALL_ONES[] = { 0xFF, 0xFF };

void test_pixel_all_ones() {
    for (int x = 0; x < 8; x++) {
        TEST_ASSERT_TRUE(spritePixelAt(ALL_ONES, 8, x, 0));
        TEST_ASSERT_TRUE(spritePixelAt(ALL_ONES, 8, x, 1));
    }
}

// ── spritePixelAt: single pixel ──

static const uint8_t SINGLE_PIXEL[] = { 0x80 }; // only x=0 set

void test_pixel_single() {
    TEST_ASSERT_TRUE(spritePixelAt(SINGLE_PIXEL, 8, 0, 0));
    TEST_ASSERT_FALSE(spritePixelAt(SINGLE_PIXEL, 8, 1, 0));
    TEST_ASSERT_FALSE(spritePixelAt(SINGLE_PIXEL, 8, 7, 0));
}

// ── spritePixelAt: last pixel ──

static const uint8_t LAST_PIXEL[] = { 0x01 }; // only x=7 set

void test_pixel_last() {
    TEST_ASSERT_FALSE(spritePixelAt(LAST_PIXEL, 8, 0, 0));
    TEST_ASSERT_FALSE(spritePixelAt(LAST_PIXEL, 8, 6, 0));
    TEST_ASSERT_TRUE(spritePixelAt(LAST_PIXEL, 8, 7, 0));
}

// ── wider sprite: 16x1 ──

static const uint8_t WIDE_SPRITE[] = { 0xF0, 0x0F }; // first 4 on, last 4 on

void test_pixel_wide_sprite() {
    // Byte 0: 0xF0 = 11110000 → x=0,1,2,3 on
    TEST_ASSERT_TRUE(spritePixelAt(WIDE_SPRITE, 16, 0, 0));
    TEST_ASSERT_TRUE(spritePixelAt(WIDE_SPRITE, 16, 3, 0));
    TEST_ASSERT_FALSE(spritePixelAt(WIDE_SPRITE, 16, 4, 0));
    TEST_ASSERT_FALSE(spritePixelAt(WIDE_SPRITE, 16, 7, 0));
    // Byte 1: 0x0F = 00001111 → x=12,13,14,15 on
    TEST_ASSERT_FALSE(spritePixelAt(WIDE_SPRITE, 16, 8, 0));
    TEST_ASSERT_FALSE(spritePixelAt(WIDE_SPRITE, 16, 11, 0));
    TEST_ASSERT_TRUE(spritePixelAt(WIDE_SPRITE, 16, 12, 0));
    TEST_ASSERT_TRUE(spritePixelAt(WIDE_SPRITE, 16, 15, 0));
}

int main() {
    UNITY_BEGIN();

    RUN_TEST(test_byte_count_8x1);
    RUN_TEST(test_byte_count_8x2);
    RUN_TEST(test_byte_count_64x32);
    RUN_TEST(test_byte_count_1x1);
    RUN_TEST(test_byte_count_non_byte_aligned);

    RUN_TEST(test_pixel_row0_on);
    RUN_TEST(test_pixel_row0_off);
    RUN_TEST(test_pixel_row1_on);
    RUN_TEST(test_pixel_row1_off);
    RUN_TEST(test_pixel_all_zeros);
    RUN_TEST(test_pixel_all_ones);
    RUN_TEST(test_pixel_single);
    RUN_TEST(test_pixel_last);
    RUN_TEST(test_pixel_wide_sprite);

    return UNITY_END();
}
