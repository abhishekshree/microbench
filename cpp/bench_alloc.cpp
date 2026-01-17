#include <string>
#include <iostream>
#include <chrono>

// Return by value triggers allocation (unless SSO works, so we make it large enough to bypass SSO if we want true malloc, but let's test small string creation first as user asked "making objects")
// Actually, Python allocates for EVERYTHING. C++ SSO optimization is a valid advantage.
// Let's make it comparable to Python: "prefix_" + number.
// This is likely small enough for SSO in some implementations (16 chars), but let's see.

std::string make_obj(int i) {
    return "prefix_" + std::to_string(i);
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < 1000000; ++i) {
        std::string t = make_obj(i);
        asm volatile("" :: "r"(&t) : "memory");
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;
    std::cout << "Time: " << diff.count() << " s" << std::endl;
    return 0;
}
