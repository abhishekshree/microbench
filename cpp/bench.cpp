#include <string>
#include <iostream>
#include <chrono>

inline const std::string& f(const std::string& x) {
    return x;
}

int main() {
    std::string s;
    s.reserve(12000000);
    for (int k = 0; k < 1000000; ++k) {
        s.append("Lorem ipsum ");
    }
    std::cout << "String length: " << s.length() << std::endl;
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < 10000000; ++i) {
        const auto& t = f(s);
        // Prevent optimization of the loop body removal
        asm volatile("" :: "r"(&t) : "memory");
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;
    std::cout << "Time: " << diff.count() << " s" << std::endl;
    return 0;
}
