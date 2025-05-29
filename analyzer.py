
import re
from gpt_modules.gpt_helper import get_gpt_suggestions
from models.finding import Finding

class DockerfileAnalyzer:
    def __init__(self, content, use_gpt=False):
        self.content = content
        self.findings = []
        self.raw_scores = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        self.use_gpt = use_gpt

    def analyze(self):
        self.findings.clear()
        self.raw_scores = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

        def add_finding(level, message, suggestion):
            self.findings.append(Finding(level, message, suggestion))
            self.raw_scores[level] += 1

        if 'USER root' in self.content:
            add_finding("HIGH", "Runs as root user", "Use non-root user")
        if 'ubuntu:latest' in self.content or 'alpine:latest' in self.content:
            add_finding("MEDIUM", "Uses 'latest' tag", "Use fixed version tag like 'ubuntu:20.04'")
        if re.search(r'ENV\s+\w*PASS\w*\s*=\s*.+', self.content):
            add_finding("HIGH", "ENV variable contains possible password", "Avoid using passwords in ENV")
        if 'ADD ' in self.content and 'COPY ' not in self.content:
            add_finding("LOW", "Using ADD instead of COPY", "Use COPY unless you need ADD features")
        if 'COPY .' in self.content or 'COPY /' in self.content:
            add_finding("MEDIUM", "Copying entire directory", "Use specific files/folders in COPY")
        if 'EXPOSE 80' in self.content:
            add_finding("MEDIUM", "Exposing port 80 without HTTPS", "Consider using EXPOSE 443")
        if 'HEALTHCHECK' not in self.content:
            add_finding("LOW", "No HEALTHCHECK defined", "Define a HEALTHCHECK for better container reliability")
        if 'apt-get install' in self.content and '--no-install-recommends' not in self.content:
            add_finding("LOW", "No install optimization", "Use --no-install-recommends to reduce image size")
        if 'rm -rf /var/lib/apt/lists' not in self.content:
            add_finding("LOW", "APT cache not cleaned", "Clean apt cache after install to reduce size")

        if 'apiVersion' in self.content and 'kind: Pod' in self.content:
            if 'securityContext:' not in self.content:
                add_finding("HIGH", "Kubernetes: securityContext block missing", "Define securityContext with proper fields")
            else:
                if 'runAsNonRoot: true' not in self.content:
                    add_finding("MEDIUM", "Kubernetes: runAsNonRoot missing", "Set runAsNonRoot: true")
                if 'readOnlyRootFilesystem: true' not in self.content:
                    add_finding("MEDIUM", "Kubernetes: readOnlyRootFilesystem missing", "Set readOnlyRootFilesystem: true")
                if 'allowPrivilegeEscalation: false' not in self.content:
                    add_finding("MEDIUM", "Kubernetes: allowPrivilegeEscalation missing", "Set allowPrivilegeEscalation: false")

        if self.use_gpt:
            self.findings.extend(get_gpt_suggestions(self.content))

        return self.findings

    def generate_fixed(self):
        fixed = self.content
        fixed = fixed.replace('USER root', 'RUN useradd -m appuser\nUSER appuser')
        fixed = fixed.replace('ubuntu:latest', 'ubuntu:20.04')
        fixed = fixed.replace('alpine:latest', 'alpine:3.18')
        fixed = re.sub(r'ENV\s+(\w*PASS\w*)\s*=.+', r'ENV \1=********', fixed)
        fixed = fixed.replace('COPY . /', 'COPY ./src /app')
        if 'securityContext:' not in fixed and 'apiVersion' in fixed:
            fixed += "\nsecurityContext:\n  runAsNonRoot: true\n  readOnlyRootFilesystem: true\n  allowPrivilegeEscalation: false"
        return fixed

    def get_score(self):
        weight = {"HIGH": 4, "MEDIUM": 2, "LOW": 1}
        raw = self.raw_scores
        total_points = (raw["HIGH"] * weight["HIGH"] +
                        raw["MEDIUM"] * weight["MEDIUM"] +
                        raw["LOW"] * weight["LOW"])
        return round(min(total_points / 20 * 10, 10))

    def get_score_breakdown(self):
        return self.raw_scores
