#include <unity.h>
#include "TimeWords.h"

using namespace pixelpulse;

// ── hourWord ──

void test_hour_word_midnight() {
    TEST_ASSERT_EQUAL_STRING("TWELVE", hourWord(0));
}

void test_hour_word_1_through_11() {
    TEST_ASSERT_EQUAL_STRING("ONE", hourWord(1));
    TEST_ASSERT_EQUAL_STRING("TWO", hourWord(2));
    TEST_ASSERT_EQUAL_STRING("THREE", hourWord(3));
    TEST_ASSERT_EQUAL_STRING("FOUR", hourWord(4));
    TEST_ASSERT_EQUAL_STRING("FIVE", hourWord(5));
    TEST_ASSERT_EQUAL_STRING("SIX", hourWord(6));
    TEST_ASSERT_EQUAL_STRING("SEVEN", hourWord(7));
    TEST_ASSERT_EQUAL_STRING("EIGHT", hourWord(8));
    TEST_ASSERT_EQUAL_STRING("NINE", hourWord(9));
    TEST_ASSERT_EQUAL_STRING("TEN", hourWord(10));
    TEST_ASSERT_EQUAL_STRING("ELEVEN", hourWord(11));
}

void test_hour_word_noon() {
    TEST_ASSERT_EQUAL_STRING("TWELVE", hourWord(12));
}

void test_hour_word_pm_maps_to_12h() {
    TEST_ASSERT_EQUAL_STRING("ONE", hourWord(13));
    TEST_ASSERT_EQUAL_STRING("ELEVEN", hourWord(23));
}

void test_hour_word_24_wraps() {
    TEST_ASSERT_EQUAL_STRING("TWELVE", hourWord(24));
}

void test_hour_word_negative() {
    TEST_ASSERT_EQUAL_STRING("ELEVEN", hourWord(-1));
}

// ── minuteWord ──

void test_minute_word_all_fives() {
    TEST_ASSERT_EQUAL_STRING("", minuteWord(0).c_str());
    TEST_ASSERT_EQUAL_STRING("FIVE PAST ", minuteWord(5).c_str());
    TEST_ASSERT_EQUAL_STRING("TEN PAST ", minuteWord(10).c_str());
    TEST_ASSERT_EQUAL_STRING("QUARTER PAST ", minuteWord(15).c_str());
    TEST_ASSERT_EQUAL_STRING("TWENTY PAST ", minuteWord(20).c_str());
    TEST_ASSERT_EQUAL_STRING("TWENTY FIVE PAST ", minuteWord(25).c_str());
    TEST_ASSERT_EQUAL_STRING("HALF PAST ", minuteWord(30).c_str());
    TEST_ASSERT_EQUAL_STRING("TWENTY FIVE TO ", minuteWord(35).c_str());
    TEST_ASSERT_EQUAL_STRING("TWENTY TO ", minuteWord(40).c_str());
    TEST_ASSERT_EQUAL_STRING("QUARTER TO ", minuteWord(45).c_str());
    TEST_ASSERT_EQUAL_STRING("TEN TO ", minuteWord(50).c_str());
    TEST_ASSERT_EQUAL_STRING("FIVE TO ", minuteWord(55).c_str());
}

void test_minute_word_rounds_non_five() {
    TEST_ASSERT_EQUAL_STRING("FIVE PAST ", minuteWord(3).c_str());
    TEST_ASSERT_EQUAL_STRING("FIVE PAST ", minuteWord(7).c_str());
    TEST_ASSERT_EQUAL_STRING("TEN PAST ", minuteWord(8).c_str());
    TEST_ASSERT_EQUAL_STRING("QUARTER PAST ", minuteWord(14).c_str());
    TEST_ASSERT_EQUAL_STRING("", minuteWord(1).c_str());
    TEST_ASSERT_EQUAL_STRING("", minuteWord(2).c_str());
}

// ── roundMinutes ──

void test_round_exact_fives() {
    TEST_ASSERT_EQUAL(0, roundMinutes(0));
    TEST_ASSERT_EQUAL(5, roundMinutes(5));
    TEST_ASSERT_EQUAL(10, roundMinutes(10));
    TEST_ASSERT_EQUAL(30, roundMinutes(30));
    TEST_ASSERT_EQUAL(55, roundMinutes(55));
}

void test_round_up() {
    TEST_ASSERT_EQUAL(5, roundMinutes(3));
    TEST_ASSERT_EQUAL(5, roundMinutes(4));
    TEST_ASSERT_EQUAL(10, roundMinutes(8));
    TEST_ASSERT_EQUAL(10, roundMinutes(9));
    TEST_ASSERT_EQUAL(15, roundMinutes(13));
}

void test_round_down() {
    TEST_ASSERT_EQUAL(0, roundMinutes(1));
    TEST_ASSERT_EQUAL(0, roundMinutes(2));
    TEST_ASSERT_EQUAL(5, roundMinutes(6));
    TEST_ASSERT_EQUAL(5, roundMinutes(7));
    TEST_ASSERT_EQUAL(50, roundMinutes(51));
    TEST_ASSERT_EQUAL(50, roundMinutes(52));
}

void test_round_wraps_at_60() {
    TEST_ASSERT_EQUAL(0, roundMinutes(58));
    TEST_ASSERT_EQUAL(0, roundMinutes(59));
}

void test_round_57_stays_55() {
    TEST_ASSERT_EQUAL(55, roundMinutes(57));
}

// ── timeToWords: o'clock ──

void test_oclock_every_hour() {
    TEST_ASSERT_EQUAL_STRING("TWELVE O'CLOCK", timeToWords(0, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("ONE O'CLOCK", timeToWords(1, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("TWO O'CLOCK", timeToWords(2, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("THREE O'CLOCK", timeToWords(3, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("FOUR O'CLOCK", timeToWords(4, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("FIVE O'CLOCK", timeToWords(5, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("SIX O'CLOCK", timeToWords(6, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("SEVEN O'CLOCK", timeToWords(7, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("EIGHT O'CLOCK", timeToWords(8, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("NINE O'CLOCK", timeToWords(9, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("TEN O'CLOCK", timeToWords(10, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("ELEVEN O'CLOCK", timeToWords(11, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("TWELVE O'CLOCK", timeToWords(12, 0).c_str());
}

void test_oclock_24h() {
    TEST_ASSERT_EQUAL_STRING("THREE O'CLOCK", timeToWords(15, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("ELEVEN O'CLOCK", timeToWords(23, 0).c_str());
}

// ── timeToWords: past ──

void test_past_all() {
    TEST_ASSERT_EQUAL_STRING("FIVE PAST THREE", timeToWords(3, 5).c_str());
    TEST_ASSERT_EQUAL_STRING("TEN PAST THREE", timeToWords(3, 10).c_str());
    TEST_ASSERT_EQUAL_STRING("QUARTER PAST NINE", timeToWords(9, 15).c_str());
    TEST_ASSERT_EQUAL_STRING("TWENTY PAST TEN", timeToWords(10, 20).c_str());
    TEST_ASSERT_EQUAL_STRING("TWENTY FIVE PAST TEN", timeToWords(10, 25).c_str());
    TEST_ASSERT_EQUAL_STRING("HALF PAST SIX", timeToWords(6, 30).c_str());
}

// ── timeToWords: to ──

void test_to_all() {
    TEST_ASSERT_EQUAL_STRING("TWENTY FIVE TO FOUR", timeToWords(3, 35).c_str());
    TEST_ASSERT_EQUAL_STRING("TWENTY TO FOUR", timeToWords(3, 40).c_str());
    TEST_ASSERT_EQUAL_STRING("QUARTER TO ELEVEN", timeToWords(10, 45).c_str());
    TEST_ASSERT_EQUAL_STRING("TEN TO FOUR", timeToWords(3, 50).c_str());
    TEST_ASSERT_EQUAL_STRING("FIVE TO TWELVE", timeToWords(11, 55).c_str());
}

void test_to_wraps_hour() {
    TEST_ASSERT_EQUAL_STRING("FIVE TO TWELVE", timeToWords(11, 55).c_str());
    TEST_ASSERT_EQUAL_STRING("FIVE TO TWELVE", timeToWords(23, 55).c_str());
    TEST_ASSERT_EQUAL_STRING("FIVE TO ONE", timeToWords(0, 55).c_str());
}

// ── timeToWords: rounding edge cases ──

void test_rounding_to_nearest_five() {
    TEST_ASSERT_EQUAL_STRING("TWENTY PAST TEN", timeToWords(10, 21).c_str());
    TEST_ASSERT_EQUAL_STRING("TWENTY FIVE PAST TEN", timeToWords(10, 23).c_str());
    TEST_ASSERT_EQUAL_STRING("TWENTY FIVE PAST TEN", timeToWords(10, 24).c_str());
    TEST_ASSERT_EQUAL_STRING("HALF PAST TEN", timeToWords(10, 28).c_str());
}

void test_58_59_wrap_to_next_hour() {
    TEST_ASSERT_EQUAL_STRING("ELEVEN O'CLOCK", timeToWords(10, 58).c_str());
    TEST_ASSERT_EQUAL_STRING("ELEVEN O'CLOCK", timeToWords(10, 59).c_str());
    TEST_ASSERT_EQUAL_STRING("ONE O'CLOCK", timeToWords(12, 58).c_str());
    TEST_ASSERT_EQUAL_STRING("TWELVE O'CLOCK", timeToWords(11, 59).c_str());
}

void test_1_2_round_to_oclock() {
    TEST_ASSERT_EQUAL_STRING("THREE O'CLOCK", timeToWords(3, 1).c_str());
    TEST_ASSERT_EQUAL_STRING("THREE O'CLOCK", timeToWords(3, 2).c_str());
}

void test_midnight_edge_cases() {
    TEST_ASSERT_EQUAL_STRING("TWELVE O'CLOCK", timeToWords(0, 0).c_str());
    TEST_ASSERT_EQUAL_STRING("TWELVE O'CLOCK", timeToWords(0, 1).c_str());
    TEST_ASSERT_EQUAL_STRING("ONE O'CLOCK", timeToWords(0, 58).c_str());
}

// ── coinIdFromSymbol ──

void test_coin_known_uppercase() {
    TEST_ASSERT_EQUAL_STRING("bitcoin", coinIdFromSymbol("BTC").c_str());
    TEST_ASSERT_EQUAL_STRING("ethereum", coinIdFromSymbol("ETH").c_str());
    TEST_ASSERT_EQUAL_STRING("solana", coinIdFromSymbol("SOL").c_str());
    TEST_ASSERT_EQUAL_STRING("cardano", coinIdFromSymbol("ADA").c_str());
    TEST_ASSERT_EQUAL_STRING("dogecoin", coinIdFromSymbol("DOGE").c_str());
    TEST_ASSERT_EQUAL_STRING("ripple", coinIdFromSymbol("XRP").c_str());
    TEST_ASSERT_EQUAL_STRING("polkadot", coinIdFromSymbol("DOT").c_str());
    TEST_ASSERT_EQUAL_STRING("litecoin", coinIdFromSymbol("LTC").c_str());
}

void test_coin_known_lowercase() {
    TEST_ASSERT_EQUAL_STRING("bitcoin", coinIdFromSymbol("btc").c_str());
    TEST_ASSERT_EQUAL_STRING("ethereum", coinIdFromSymbol("eth").c_str());
    TEST_ASSERT_EQUAL_STRING("dogecoin", coinIdFromSymbol("doge").c_str());
}

void test_coin_unknown_lowercases() {
    TEST_ASSERT_EQUAL_STRING("shib", coinIdFromSymbol("SHIB").c_str());
    TEST_ASSERT_EQUAL_STRING("avax", coinIdFromSymbol("AVAX").c_str());
    TEST_ASSERT_EQUAL_STRING("matic", coinIdFromSymbol("MATIC").c_str());
}

void test_coin_empty() {
    TEST_ASSERT_EQUAL_STRING("", coinIdFromSymbol("").c_str());
}

void test_coin_single_char() {
    TEST_ASSERT_EQUAL_STRING("x", coinIdFromSymbol("X").c_str());
}

int main() {
    UNITY_BEGIN();

    RUN_TEST(test_hour_word_midnight);
    RUN_TEST(test_hour_word_1_through_11);
    RUN_TEST(test_hour_word_noon);
    RUN_TEST(test_hour_word_pm_maps_to_12h);
    RUN_TEST(test_hour_word_24_wraps);
    RUN_TEST(test_hour_word_negative);

    RUN_TEST(test_minute_word_all_fives);
    RUN_TEST(test_minute_word_rounds_non_five);

    RUN_TEST(test_round_exact_fives);
    RUN_TEST(test_round_up);
    RUN_TEST(test_round_down);
    RUN_TEST(test_round_wraps_at_60);
    RUN_TEST(test_round_57_stays_55);

    RUN_TEST(test_oclock_every_hour);
    RUN_TEST(test_oclock_24h);
    RUN_TEST(test_past_all);
    RUN_TEST(test_to_all);
    RUN_TEST(test_to_wraps_hour);
    RUN_TEST(test_rounding_to_nearest_five);
    RUN_TEST(test_58_59_wrap_to_next_hour);
    RUN_TEST(test_1_2_round_to_oclock);
    RUN_TEST(test_midnight_edge_cases);

    RUN_TEST(test_coin_known_uppercase);
    RUN_TEST(test_coin_known_lowercase);
    RUN_TEST(test_coin_unknown_lowercases);
    RUN_TEST(test_coin_empty);
    RUN_TEST(test_coin_single_char);

    return UNITY_END();
}
