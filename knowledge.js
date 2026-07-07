const TOPICS = [
  { id:"quantum-physics", title:"Quantum Physics", summary:"The study of matter and energy at the most fundamental level…", difficulty:"Advanced", key_concepts:["superposition","entanglement","wave-particle duality"], related_topics:["physics","wave theory","particle physics"], image:"" },
  { id:"football", title:"Football (Soccer)", summary:"The world's most popular sport…", difficulty:"Beginner", key_concepts:["offside","penalty kick","formation"], related_topics:["sports science","athletics","team strategy"], image:"" },
  { id:"machine-learning", title:"Machine Learning", summary:"A branch of AI where systems learn from data…", difficulty:"Advanced", key_concepts:["neural networks","gradient descent","overfitting"], related_topics:["deep learning","data science","ai ethics"], image:"" },
  { id:"cyber-security", title:"Cyber Security", summary:"Protecting systems, networks, and programs from digital attacks…", difficulty:"Intermediate", key_concepts:["encryption","firewall","phishing"], related_topics:["network security","cryptography","ethical hacking"], image:"" },
  { id:"photosynthesis", title:"Photosynthesis", summary:"The process by which green plants convert sunlight…", difficulty:"Intermediate", key_concepts:["chlorophyll","Calvin cycle","light reactions"], related_topics:["biology","plant science","carbon cycle"], image:"" },
];

function findTopic(query) {
  const q = query.toLowerCase().trim();
  return TOPICS.find(t => t.title.toLowerCase() === q) ||
         TOPICS.find(t => t.title.toLowerCase().includes(q)) ||
         TOPICS.find(t => t.key_concepts.some(c => c.toLowerCase().includes(q))) ||
         null;
}

module.exports = { TOPICS, findTopic };