fn first_word(s: &String) -> usize {
    let bytes = s.as_bytes();
    println!("{:}",bytes[0]);

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return i;
        }
    }

    s.len()
}

fn main() {
    let mut s = String::from("hello world");

    println!("{}",s);
    let word = first_word(&s); // word will get the value 5
    println!("{}",word);
    s.clear(); // this empties the String, making it equal to ""

    // word still has the value 5 here, but there's no more string that
    // we could meaningfully use the value 5 with. word is now totally invalid!
}
