use std::time::Instant;
use std::hint::black_box;

fn make_obj(i: i32) -> String {
    format!("prefix_{}", i)
}

fn main() {
    let start = Instant::now();
    for i in 0..1_000_000 {
        let t = make_obj(i);
        black_box(t);
    }
    let duration = start.elapsed();
    println!("Time: {:.6} s", duration.as_secs_f64());
}
