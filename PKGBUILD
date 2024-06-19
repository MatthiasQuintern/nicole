# Maintainer: Matthias Quintern <matthias(dot)quintern(at)posteo(dot)de>
pkgname=nicole
pkgver=2.1.1
pkgrel=3
pkgdesc="Write lyrics from genius or azlyrics.com to a mp3-tag"
arch=('any')
url="https:/github.com/MatthiasQuintern/nicole"
license=('GPL3')
depends=('python-mutagen' 'python-beautifulsoup4')
source=(file://${PWD}/nicole/nicole.py _nicole.compdef.zsh nicole.1.man)
md5sums=('b72bfd6aefe9c1f28015f896c64535ad'
         '52e446aa13ae481eece1935bceece193'
         '4ad29357b608c88eebc49546a50e489d')

package() {
	mkdir -p "${pkgdir}/usr/bin"
	cp "${srcdir}/nicole.py" "${pkgdir}/usr/bin/nicole"
	chmod +x "${pkgdir}/usr/bin/nicole"

	mkdir -p "${pkgdir}/usr/share/man/man1/"
	cp "${srcdir}/nicole.1.man" "${pkgdir}/usr/share/man/man1/nicole.1"

	# if zsh is installed
	if [[ -f /bin/zsh ]]; then
		mkdir -p "${pkgdir}/usr/share/zsh/site-functions"
		cp "${srcdir}/_nicole.compdef.zsh" "${pkgdir}/usr/share/zsh/site-functions/_nicole"
		chmod +x "${pkgdir}/usr/share/zsh/site-functions/_nicole"
	fi
}
