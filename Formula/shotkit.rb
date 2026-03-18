class Shotkit < Formula
  desc "App Store screenshot pipeline: auto-capture, trending styles, ASC integration"
  homepage "https://github.com/nicolocurioni96/withnico-skills"
  url "https://github.com/nicolocurioni96/withnico-skills/archive/refs/tags/v2.0.0.tar.gz"
  sha256 "41659c9105da1e3d88a171a46f894b10d5e3c732530fbb634ca423e61636b8aa"
  license "MIT"
  version "2.0.0"

  depends_on :macos
  depends_on "python@3"

  def install
    # Install scripts to libexec
    libexec.install Dir["skills/shotkit/scripts/*"]
    (libexec/"assets/fonts").mkpath
    libexec.install "skills/shotkit/references"

    # Install Python dependencies into libexec
    venv = libexec/"vendor"
    system "python3", "-m", "venv", venv.to_s
    venv_pip = venv/"bin/pip3"
    system venv_pip.to_s, "install", "Pillow", "PyJWT", "cryptography"

    # Create wrapper that sets up PATH to use venv python
    (bin/"shotkit").write <<~EOS
      #!/bin/bash
      export PATH="#{libexec}/vendor/bin:$PATH"
      exec "#{libexec}/shotkit" "$@"
    EOS
  end

  test do
    assert_match "shotkit", shell_output("#{bin}/shotkit --version")
  end
end
