#include <array>
#include <bitset>

#include "msl/fwcounter.h"
#include "ooo_cpu.h"


namespace {
constexpr std::size_t COUNTER_BITS = 2;
constexpr std::size_t GLOBAL_BHR_SIZE = 16;
constexpr std::size_t GLOBAL_PHT_SIZE = 1 << GLOBAL_BHR_SIZE;

std::bitset<GLOBAL_BHR_SIZE> global_bhr;
std::array<champsim::msl::fwcounter<COUNTER_BITS>, GLOBAL_PHT_SIZE> global_pht;
} // namespace

void O3_CPU::initialize_branch_predictor() {
    std::cout << "CPU " << cpu << " GAg branch predictor" << std::endl;
}

uint8_t O3_CPU::predict_branch(uint64_t ip) {
    auto value = ::global_pht[::global_bhr.to_ulong()];
    return value.value() >= (value.maximum / 2);
}

void O3_CPU::last_branch_result(uint64_t ip, uint64_t branch_target, uint8_t taken, uint8_t branch_type) {
    // update PHT
    ::global_pht[::global_bhr.to_ulong()] += taken ? 1 : -1;
    // update BHR
    ::global_bhr <<= 1;
    ::global_bhr[0] = taken;
}
