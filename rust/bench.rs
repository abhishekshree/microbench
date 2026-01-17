use std::time::Instant;
use std::hint::black_box;

#[inline]
fn f(x: &String) -> &String {
    x
}

fn main() {
    let s = "Lorem ipsum ".repeat(1_000_000);
    println!("String length: {}", s.len());
    let start = Instant::now();
    for _ in 0..10_000_000 {
        let t = f(&s);
        black_box(t);
    }
    let duration = start.elapsed();
    println!("Time: {:.6} s", duration.as_secs_f64());
}
