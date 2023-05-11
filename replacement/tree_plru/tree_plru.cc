#include <algorithm>
#include <list>
#include <map>
#include <memory>
#include <vector>

#include "cache.h"


namespace {
class Node {
public:
    explicit Node(uint32_t v) : victimIdx{v} {}
    Node() = default;

    auto GetLeft() {
        return left;
    }
    auto GetRight() {
        return right;
    }
    auto GetNext() {
        SwitchDirection();
        return goRight ? left : right;
    }
    void SwitchDirection() {
        goRight = !goRight;
    }

    void SetLeft(std::shared_ptr<Node> node) {
        left = node;
    }
    void SetRight(std::shared_ptr<Node> node) {
        right = node;
    }

    bool IsLeaf() const {
        return victimIdx != INVALID_WAY_IDX;
    }
    auto GetVictimIdx() const {
        return victimIdx;
    }

private:
    static constexpr uint32_t INVALID_WAY_IDX = static_cast<uint32_t>(0) - 1;

private:
    std::shared_ptr<Node> left{nullptr};
    std::shared_ptr<Node> right{nullptr};
    // initialize to choose the left descendant
    bool goRight{false};
    uint32_t victimIdx{INVALID_WAY_IDX};
};

constexpr bool isPowerOfTwo(uint64_t n) {
    return (n & (n - 1)) == 0;
}

std::map<CACHE*, std::vector<std::shared_ptr<Node>>> forests;

void initForest(std::vector<std::shared_ptr<Node>> &forest, std::size_t numSet, std::size_t numWay) {
    assert(isPowerOfTwo(numWay));
    forest.reserve(numSet);

    for (size_t i = 0; i < numSet; ++i) {
        auto root = std::make_shared<Node>();
        forest.push_back(root);
        std::list<std::shared_ptr<Node>> pending{root};

        auto endDepth = __builtin_ctz(numWay) - 1;
        for (int j = 0; j < endDepth; ++j) {
            for (int k = 0, endWidth = 1 << j; k < endWidth; ++k) {
                auto parent = pending.front();
                pending.pop_front();

                auto left = std::make_shared<Node>();
                auto right = std::make_shared<Node>();
                parent->SetLeft(left);
                parent->SetRight(right);
                pending.push_back(left);
                pending.push_back(right);
            }
        }

        assert(pending.size() == numWay / 2);
        std::size_t idx = 0;
        for (auto &it : pending) {
            it->SetLeft(std::make_shared<Node>(idx++));
            it->SetRight(std::make_shared<Node>(idx++));
        }
    }
}

uint32_t findVictim(std::vector<std::shared_ptr<Node>> &forest, uint32_t set) {
    auto node = forest.at(set);
    while (!node->IsLeaf()) {
        node = node->GetNext();
    }
    return node->GetVictimIdx();
}

void updateOnMiss(std::vector<std::shared_ptr<Node>> &forest, uint32_t set, uint32_t way) {
    auto node = forest.at(set);
    while (!node->IsLeaf()) {
        auto goRight = ((way & 1) == 1);
        auto tmp = goRight ? node->GetRight() : node->GetLeft();
        way >>= 1;

        node->SwitchDirection();
        node = tmp;
    }
}
}   // namespace


void CACHE::initialize_replacement() {
    ::initForest(::forests[this], NUM_SET, NUM_WAY);
}

uint32_t CACHE::find_victim(uint32_t triggering_cpu, uint64_t instr_id, uint32_t set, const BLOCK* current_set, uint64_t ip, uint64_t full_addr, uint32_t type) {
    return ::findVictim(::forests[this], set);
}

void CACHE::update_replacement_state(uint32_t triggering_cpu, uint32_t set, uint32_t way, uint64_t full_addr, uint64_t ip, uint64_t victim_addr, uint32_t type,
                                     uint8_t hit) {
    // Find the way while flipping nodes' directions
    if (!hit || type != WRITE) {    // Skip this for writeback hits
        ::updateOnMiss(::forests[this], set, way);
    }
}

void CACHE::replacement_final_stats() {
}
