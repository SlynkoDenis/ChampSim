#include <array>
#include <map>
#include <unordered_map>

#include "msl/fwcounter.h"
#include "ooo_cpu.h"


namespace {
constexpr std::size_t COUNTER_BITS = 2;
constexpr std::size_t GLOBAL_BHR_SIZE = 14;
constexpr std::size_t PER_BRANCH_PHT_SIZE = 1 << GLOBAL_BHR_SIZE;

using per_branch_pht_type =
    std::unordered_map<uint64_t,
                       std::array<champsim::msl::fwcounter<COUNTER_BITS>, PER_BRANCH_PHT_SIZE>>;

std::bitset<GLOBAL_BHR_SIZE> global_bhr;
std::map<O3_CPU*, per_branch_pht_type> per_branch_pht;
} // namespace

void O3_CPU::initialize_branch_predictor() {
    std::cout << "CPU " << cpu << " GAp branch predictor" << std::endl;
}

uint8_t O3_CPU::predict_branch(uint64_t ip) {
    auto value = ::per_branch_pht[this][ip][::global_bhr.to_ulong()];
    return value.value() >= (value.maximum / 2);
}

void O3_CPU::last_branch_result(uint64_t ip, uint64_t branch_target, uint8_t taken, uint8_t branch_type) {
    // update PHT
    ::per_branch_pht[this][ip][::global_bhr.to_ulong()] += taken ? 1 : -1;
    // update BHR
    ::global_bhr <<= 1;
    ::global_bhr[0] = taken;
}
