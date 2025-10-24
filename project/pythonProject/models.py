class Resource:
    def __init__(self, title, author, level, rtype, url, alignment):
        self.title = title
        self.author = author
        self.level = level  # ex: "High School", "College"
        self.rtype = rtype  # ex: "Tutorial", "Article"
        self.url = url
        self.alignment = alignment  # ex: {"framework": "CS Curriculum", "target": "Data Structures"}

    def to_jsonld(self):
        return {
            "@context": "https://schema.org/",
            "@type": "LearningResource",
            "name": self.title,
            "educationalLevel": self.level,
            "learningResourceType": self.rtype,
            "url": self.url,
            "author": {
                "@type": "Person",
                "name": self.author
            },
            "educationalAlignment": {
                "@type": "AlignmentObject",
                "alignmentType": "teaches",
                "educationalFramework": self.alignment["framework"],
                "targetName": self.alignment["target"]
            }
        }
